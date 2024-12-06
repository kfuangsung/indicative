from collections import deque
from typing import Any, Callable, Iterable, TypeVar

from multimethod import multimethod
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from .datas import PriceDataArray
from .protocols import NamedTupleProtocol

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Record[T]:
    name: str
    data: deque[T] = Field(default_factory=deque)
    size: PositiveInt | None = Field(default=None)

    def __call__(self, item: T | Iterable[T]) -> None:
        return self.append(item)

    def __getitem__(self, index: int) -> T:
        return self.data[index]

    def reset(self) -> None:
        self.data.clear()

    @multimethod
    def append(self, item: T) -> None:
        self.data.append(item)
        self.adjust_size()

    @append.register
    def _(self, items: Iterable[T]) -> None:
        self.data.extend(items)
        self.adjust_size()

    def get_oldest(self) -> T:
        return self.data[0]

    def get_latest(self) -> T:
        return self.data[-1]

    def pop_oldest(self) -> T:
        return self.data.popleft()

    def pop_latest(self) -> T:
        return self.data.pop()

    def adjust_size(self) -> None:
        if self.size is None:
            return
        while len(self.data) > self.size:
            self.data.popleft()

    get = get_latest
    pop = pop_oldest


# general purposed history -> store anything
@dataclass
class History[T]:
    default_size: PositiveInt | None = Field(default=None)

    @property
    def records(self) -> list[Record[T]]:
        return list(filter(lambda x: isinstance(x, Record[T]), self.__dict__.values()))

    def __getitem__(self, name) -> Record[T]:
        return self.__dict__[name]

    def __or__(self, other: Callable):
        return other(self)

    def __ror__(self, other, *args, **kwargs):
        return self.register(other, *args, **kwargs)

    @multimethod
    def register(
        self,
        name: str,
        data: Iterable | None = None,
        size: int | None = None,
        replace: bool | None = False,
    ) -> None:
        # if exists then extend
        if name in self.__dict__ and not replace:
            self.__dict__[name].append(data)
            return

        record = Record(name=name, size=size or self.default_size)
        if data is not None:
            record.append(data)

        self.__dict__[name] = record

    @register.register
    def _(
        self,
        name: str,
        data: int | float | str = None,
        size: int | None = None,
        replace: bool | None = False,
    ) -> None:
        return self.register(name, [data], size, replace)

    @register.register
    def _(self, name, record: Record, replace: bool | None = False) -> None:
        return self.register(name, record.data, record.size, replace)

    @register.register
    def _(self, record: Record, replace: bool | None = False) -> None:
        return self.register(record.name, record, replace)

    @register.register
    def _(
        self,
        dictionary: dict[str, Any],
        size: int | None = None,
        replace: bool | None = False,
    ) -> None:
        for k, v in dictionary.items():
            self.register(k, v, size or self.default_size, replace)
        return

    @register.register
    def _(
        self,
        namedtuple: NamedTupleProtocol,
        size: int | None = None,
        replace: bool | None = False,
    ) -> None:
        return self.register(namedtuple._asdict(), size, replace)

    @register.register
    def _(
        self,
        namedtuple_list: Iterable[NamedTupleProtocol],
        size: int | None = None,
        replace: bool | None = False,
    ) -> None:
        for nt in namedtuple_list:
            self.register(nt, size, replace)

    @register.register
    def _(
        self,
        price_data_arr: PriceDataArray,
        size: int | None = None,
        replace: bool | None = False,
    ):
        self.register(price_data_arr.__dict__, size, replace)
