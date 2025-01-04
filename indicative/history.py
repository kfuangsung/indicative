from collections import deque
from collections.abc import Callable, Iterable
from typing import Any, Self, TypeVar

from multimethod import multimethod
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from .datas import PriceDataArray, PriceDataPoint
from .protocols import NamedTupleProtocol

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Record[T]:
    """A record is an immutable data structure that stores a sequence of values.

    Attributes:
        name (str): The name of the record.
        data (deque[T]): The sequence of values stored in the record.
        size (PositiveInt | None): The maximum number of values to store in the record.
    """

    name: str
    data: deque[T] = Field(default_factory=deque)
    size: PositiveInt | None = Field(default=None)

    def __call__(self, item: T | Iterable[T]) -> None:
        """Append a value or a sequence of values to the record.

        Args:
            item (T | Iterable[T]): The value or sequence of values to append.
        """
        return self.append(item)

    def __getitem__(self, key: int) -> T | list[T]:
        """Get a value from the record by index.

        Args:
            key (int): The index of the value to retrieve.

        Returns:
            T | list[T]: The value at the specified index, or a list of values
                if the index is a slice.
        """
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.data)))
            return [self.data[i] for i in indices]
        return self.data[key]

    def __len__(self) -> int:
        """Get the number of values in the record.

        Returns:
            int: The number of values in the record.
        """
        return len(self.data)

    def at(self, index: int) -> T:
        """Get a value from the record by index.

        Args:
            index (int): The index of the value to retrieve.

        Returns:
            T: The value at the specified index.
        """
        return self.data[index]

    def front(self) -> T:
        """Get the first value from the record.

        Returns:
            T: The first value in the record.
        """
        return self.data[0]

    def back(self) -> T:
        """Get the last value from the record.

        Returns:
            T: The last value in the record.
        """
        return self.data[-1]

    def reset(self) -> None:
        """Reset the record to an empty sequence.

        Returns:
            None
        """
        self.data.clear()

    @multimethod
    def append(self, item: T) -> None:
        """Append a value to the record.

        Args:
            item (T): The value to append.
        """
        self.data.append(item)
        self.adjust_size()

    @append.register  # type: ignore
    def _(self, items: Iterable[T]) -> None:
        """Append a sequence of values to the record.

        Args:
            items (Iterable[T]): The sequence of values to append.
        """
        self.data.extend(items)
        self.adjust_size()

    def get_oldest(self) -> T:
        """Get the oldest value from the record.

        Returns:
            T: The oldest value in the record.
        """
        return self.data[0]

    def get_latest(self) -> T:
        """Get the latest value from the record.

        Returns:
            T: The latest value in the record.
        """
        return self.data[-1]

    def pop_oldest(self) -> T:
        """Pop the oldest value from the record.

        Returns:
            T: The oldest value in the record.
        """
        return self.data.popleft()

    def pop_latest(self) -> T:
        """Pop the latest value from the record.

        Returns:
            T: The latest value in the record.
        """
        return self.data.pop()

    def adjust_size(self) -> None:
        """Adjust the size of the record by removing the oldest values until the
        record is at or below the maximum size.

        Returns:
            None
        """
        if self.size is None:
            return
        while len(self.data) > self.size:
            self.data.popleft()

    get = get_latest
    pop = pop_oldest


@dataclass
class History[T]:
    """A general purposed history -> store anything.

    Allows to register data into the history with a given name, and access
    the data by name.

    Attributes:
        default_size: The default size of the record.
    """

    default_size: PositiveInt | None = Field(default=1000)

    @property
    def records(self) -> list[Record[T]]:
        """Gets the records from the history.

        Returns:
            list[Record[T]]: The records in the history.
        """
        return list(filter(lambda x: isinstance(x, Record), self.__dict__.values()))

    @property
    def fields(self) -> list[str]:
        """Gets the field names from the history.

        Returns:
            list[str]: The field names in the history.
        """
        return [record.name for record in self.records]

    def __getitem__(self, name: str) -> Record[T]:
        """Accesses a record by its name.

        Args:
            name (str): The name of the record.

        Returns:
            Record[T]: The record associated with the given name.
        """
        return self.__dict__[name]

    def __or__(self, other: Callable):
        """Allows using the `|` operator for applying a callable to the history.

        Args:
            other (Callable): The callable to be applied.

        Returns:
            Any: The result of applying the callable to the history.
        """
        return other(self)

    def __ror__(self, other: Any, *args, **kwargs) -> Self:
        """Allows using the `|` operator to register data into the history.

        Args:
            other (Any): The data to be registered.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Self: The updated history.
        """
        self.register(other, *args, **kwargs)
        return self

    @multimethod
    def register(
        self,
        name: str,
        data: Iterable[Any] = [],
        size: int | None = None,
        replace: bool = False,
    ) -> None:
        """Registers data into the history with a given name.

        Args:
            name (str): The name of the record.
            data (Iterable[Any], optional): The data to be registered. Defaults to [].
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        if name in self.__dict__ and not replace:
            self.__dict__[name].append(data)
            return

        record = Record(name=name, size=size or self.default_size)
        if data is not None:
            record.append(data)

        self.__dict__[name] = record

    @register.register  # type: ignore
    def _(
        self,
        name: str,
        data: Any,
        size: int | None = None,
        replace: bool = False,
    ) -> None:
        """Registers data into the history with a given name.

        Args:
            name (str): The name of the record.
            data (Any): The data to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        return self.register(name, [data], size, replace)

    @register.register  # type: ignore
    def _(self, name, record: Record, replace: bool = False) -> None:
        """Registers a record into the history with a given name.

        Args:
            name (str): The name of the record.
            record (Record): The record to be registered.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        return self.register(name, record.data, record.size, replace)

    @register.register  # type: ignore
    def _(self, record: Record, replace: bool = False) -> None:
        """Registers a record into the history.

        Args:
            record (Record): The record to be registered.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        return self.register(record.name, record, replace)

    @register.register  # type: ignore
    def _(
        self,
        dictionary: dict[str, Any],
        size: int | None = None,
        replace: bool = False,
    ) -> None:
        """Registers a dictionary of data into the history.

        Args:
            dictionary (dict[str, Any]): The dictionary of data to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        for k, v in dictionary.items():
            self.register(k, v, size or self.default_size, replace)
        return

    @register.register  # type: ignore
    def _(
        self,
        namedtuple: NamedTupleProtocol,
        size: int | None = None,
        replace: bool = False,
    ) -> None:
        """Registers a namedtuple into the history.

        Args:
            namedtuple (NamedTupleProtocol): The namedtuple to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        return self.register(namedtuple._asdict(), size, replace)

    @register.register  # type: ignore
    def _(
        self,
        namedtuple_list: Iterable[NamedTupleProtocol],
        size: int | None = None,
        replace: bool = False,
    ) -> None:
        """Registers a list of namedtuples into the history.

        Args:
            namedtuple_list (Iterable[NamedTupleProtocol]): The list of namedtuples to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        for nt in namedtuple_list:
            self.register(nt, size, replace)

    @register.register  # type: ignore
    def _(
        self,
        price_data_arr: PriceDataArray,
        size: int | None = None,
        replace: bool = False,
    ):
        """Registers a PriceDataArray into the history.

        Args:
            price_data_arr (PriceDataArray): The PriceDataArray to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        self.register(price_data_arr.__dict__, size, replace)

    @register.register  # type: ignore
    def _(
        self,
        price_data_pnt: PriceDataPoint,
        size: int | None = None,
        replace: bool = False,
    ):
        """Registers a PriceDataPoint into the history.

        Args:
            price_data_pnt (PriceDataPoint): The PriceDataPoint to be registered.
            size (int | None, optional): The size of the record. Defaults to None.
            replace (bool, optional): Whether to replace existing data. Defaults to False.
        """
        self.register(price_data_pnt.__dict__, size, replace)
