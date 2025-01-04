from collections.abc import Callable, Sequence, Iterable
from typing import Any, TypeVar

import numpy as np
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from .mixins import AdapterMixin, SelectMixin
from .protocols import AdapterProtocol

__all__ = [
    "Select",
    "Transform",
    "Filter",
    "Head",
    "Tail",
    "Attr",
    "Mean",
    "Reverse",
    "Sort",
]


T = TypeVar("T")


@dataclass
class Select[T](AdapterProtocol, AdapterMixin):
    """Select adapter.

    Select adapter calls the provided function with the input sequence and
    returns the result.

    Args:
        func: A callable that takes a sequence and returns a value.

    Returns:
        The result of calling the provided function with the input sequence.

    Example:
        >>> adapter = Select(lambda x: x[0])
        >>> [1, 2, 3] | adapter
        1
    """

    func: Callable[[Sequence[T]], Any]

    def __ror__(self, other: Sequence[T]) -> Any:
        """Pipeline magic method.

        Args:
            other: The input sequence.

        Returns:
            The result of calling the provided function with the input sequence.
        """
        return self.func(other)


@dataclass
class Transform[T](AdapterProtocol, AdapterMixin):
    """Transform adapter.

    The Transform adapter applies the provided function to each element in the
    input sequence and returns the result.

    Args:
        func: A callable that takes a single element and returns a value.

    Returns:
        The result of calling the provided function with each element in the
        input sequence.

    Example:
        >>> adapter = Transform(lambda x: x**2)
        >>> [1, 2, 3] | adapter
        [1, 4, 9]
    """

    func: Callable[[Sequence[T]], Sequence[T]]

    def __ror__(self, other: Iterable[Any]) -> list[Sequence[T]]:
        """Pipeline magic method.

        Args:
            other: The input sequence.

        Returns:
            The result of calling the provided function with each element in the
            input sequence.
        """
        return list(map(self.func, other))


@dataclass
class Filter[T](  # pylint: disable=invalid-name
    AdapterProtocol, AdapterMixin
):
    """Filter adapter.

    The Filter adapter applies the provided function to each element in the
    input sequence and returns the result.

    Args:
        func: A callable that takes a single element and returns a boolean.

    Returns:
        The list of elements in the input sequence for which the provided
        function returns True.

    Example:
        >>> adapter = Filter(lambda x: x > 0)
        >>> [1, -2, 3] | adapter
        [1, 3]
    """

    func: Callable[[Sequence[T]], Sequence[T]]

    def __ror__(self, other: Iterable[Any]) -> list[Any]:
        """Pipeline magic method.

        Args:
            other: The input sequence.

        Returns:
            The list of elements in the input sequence for which the provided
            function returns True.
        """
        return list(filter(self.func, other))


@dataclass
class Head(SelectMixin[T]):
    """Selects the first `n` elements from a sequence.

    Attributes:
        n (PositiveInt): The number of elements to select from the start of the sequence.
    """

    n: PositiveInt = Field(default=10)

    def __post_init__(self) -> None:
        """Initializes the selection function."""
        self.select = Select(lambda x: x[: self.n])


@dataclass
class Tail(SelectMixin[T]):
    """Selects the last `n` elements from a sequence.

    Attributes:
        n: The number of elements to select from the end of the sequence.
    """

    n: PositiveInt = Field(default=10)

    def __post_init__(self) -> None:
        """Initializes the selection function to select the last `n` elements."""
        self.select = Select(lambda x: x[-self.n :])


@dataclass
class Front(SelectMixin[T]):
    """Selects the first element from a sequence.

    This adapter selects and returns the first element of the input sequence.

    Attributes:
        select: A Select object initialized to select the first element.
    """

    def __post_init__(self) -> None:
        """Initializes the selection function to select the first element."""
        self.select = Select(lambda x: x[0])


@dataclass
class Back(SelectMixin[T]):
    """Selects the last element from a sequence.

    This adapter selects and returns the last element of the input sequence.

    Attributes:
        select: A Select object initialized to select the last element.
    """

    def __post_init__(self) -> None:
        """Initializes the selection function to select the last element."""
        self.select = Select(lambda x: x[-1])


@dataclass
class Attr(SelectMixin[T]):
    """Selects an attribute from each element in a sequence.

    This adapter uses the specified attribute name to extract the attribute's value from each element in the input sequence.

    Attributes:
        attr (str): The name of the attribute to be selected from each element.
    """

    attr: str

    def __post_init__(self) -> None:
        """Initializes the selection function to extract the specified attribute."""
        self.select = Select(lambda x: getattr(x, self.attr))


@dataclass
class Mean(SelectMixin[T]):
    """Computes the mean of a sequence of numbers.

    This adapter takes a sequence of numbers as input and returns the mean of the
    sequence.

    Examples:
        >>> [1, 2, 3, 4, 5] | Mean()
        3.0

    Attributes:
        select (Select): The selection function to compute the mean.
    """

    def __post_init__(self) -> None:
        """Initializes the selection function to compute the mean."""
        self.select = Select(lambda x: np.mean(np.asarray(x)))


@dataclass
class Reverse(SelectMixin[T]):
    """Reverses the order of the elements in a sequence.

    This adapter takes a sequence as input and returns a new sequence with the elements in reverse order.

    Examples:
        >>> [1, 2, 3, 4, 5] | Reverse()
        [5, 4, 3, 2, 1]
    """

    def __post_init__(self) -> None:
        """Initializes the selection function to reverse the sequence."""
        self.select = Select(lambda x: list(reversed(list(x))))


@dataclass
class Sort(SelectMixin[T]):
    """Sorts the elements in a sequence.

    This adapter sorts the elements in the input sequence in ascending or
    descending order based on the `reverse` attribute.

    Attributes:
        reverse (bool): If True, sort the sequence in descending order.
                        Defaults to False.
    """

    reverse: bool = Field(default=False)

    def __post_init__(self) -> None:
        """Initializes the selection function to sort the sequence."""
        self.select = Select(lambda x: sorted(list(x), reverse=self.reverse))
