from typing import Any, Callable, Iterable, TypeVar

import numpy as np
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from .mixins import AdapterMixin, SelectMixin
from .protocols import AdapterProtocol

T = TypeVar("T")


@dataclass
class Select[T](AdapterProtocol, AdapterMixin):
    func: Callable[[Iterable[T]], Any]

    def __ror__(self, other: Iterable[T]) -> Any:
        return self.func(other)


@dataclass
class Transform[T](AdapterProtocol, AdapterMixin):
    func: Callable[[Iterable[T]], Iterable[T]]

    def __ror__(self, other: Iterable[T]) -> Iterable[T]:
        return list(map(self.func, other))


@dataclass
class Filter[T](AdapterProtocol, AdapterMixin):
    func: Callable[[Iterable[T]], Iterable[T]]

    def __ror__(self, other: Iterable[T]) -> list[T]:
        return list(filter(self.func, other))


@dataclass
class Head(SelectMixin[T]):
    n: PositiveInt = Field(default=10)

    def __post_init__(self) -> None:
        self.select = Select(lambda x: x[: self.n])


@dataclass
class Tail(SelectMixin[T]):
    n: PositiveInt = Field(default=10)

    def __post_init__(self) -> None:
        self.select = Select(lambda x: x[-self.n :])


@dataclass
class Attr(SelectMixin[T]):
    attr: str

    def __post_init__(self) -> None:
        self.select = Select(lambda x: getattr(x, self.attr))


@dataclass
class Mean(SelectMixin[T]):
    def __post_init__(self) -> None:
        self.select = Select(lambda x: np.mean(x))


@dataclass
class Reverse(SelectMixin[T]):
    def __post_init__(self) -> None:
        self.select = Select(lambda x: list(reversed(x)))


@dataclass
class Sort(SelectMixin[T]):
    reverse: bool = Field(default=False)

    def __post_init__(self) -> None:
        self.select = Select(lambda x: sorted(x, reverse=self.reverse))
