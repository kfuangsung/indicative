from collections.abc import Iterable
from typing import Any


class IndicatorMixin:
    """A mixin class for indicators.

    It provides a `__call__` method that calls the `compute` method of the
    indicator and a `__ror__` method that calls the indicator with the given
    arguments.

    Attributes:
        compute: A method that computes the indicator.
    """

    def __call__(self, *args, **kwargs) -> Any:
        """Calls the `compute` method of the indicator.

        Args:
            *args: The positional arguments to pass to the `compute` method.
            **kwargs: The keyword arguments to pass to the `compute` method.

        Returns:
            The result of calling the `compute` method.
        """
        return self.compute(*args, **kwargs)  # type: ignore

    def __ror__(self, other: Iterable):
        """Calls the indicator with the given arguments.

        Args:
            other: The arguments to pass to the indicator.

        Returns:
            The result of calling the indicator with the given arguments.
        """
        return self(other)


class AdapterMixin:
    """A mixin class that provides a `__call__` method to call a stored function.

    The `__call__` method calls the stored function with the provided arguments.

    Attributes:
        func: The stored function.
    """

    def __call__(self, *args, **kwargs):
        """Call the stored function with the provided arguments.

        Args:
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The result of calling the function.
        """
        return self.func(*args, **kwargs)  # type: ignore


class SelectMixin[T]:
    """A mixin that provides a `__call__` method to call a stored selection function.

    The `__call__` method calls the stored selection function with the provided
    arguments.

    Attributes:
        select: The stored selection function.
    """

    def __call__(self, *args, **kwargs):
        """Call the stored selection function with the provided arguments.

        Args:
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The result of calling the function.
        """
        return self.select(*args, **kwargs)  # type: ignore

    def __ror__(self, other: Iterable[T]) -> Any:
        """Call the stored selection function with the given iterable.

        Args:
            other: The iterable to pass to the function.

        Returns:
            Any: The result of calling the function.
        """
        return self.select(other)  # type: ignore
