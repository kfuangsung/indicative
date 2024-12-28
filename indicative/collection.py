from collections.abc import Callable
from typing import Any

from pydantic.dataclasses import dataclass


@dataclass
class Collection:
    """A collection of functions that can be called in parallel.

    Attributes:
        fns: A tuple of callables.

    Returns:
        A list of results from calling each function in `fns` with the same arguments.
    """

    fns: tuple[Callable[[Any], Any], ...]

    def __call__(self, *args, **kwargs):
        """Calls each function in `fns` with the same arguments.

        Args:
            *args: The positional arguments to pass to each function.
            **kwargs: The keyword arguments to pass to each function.

        Returns:
            A list of results from calling each function in `fns`.
        """
        return [f(*args, **kwargs) for f in self.fns]

    def __ror__(self, other: Any) -> Any:
        """Allows using the `|` operator for calling the functions in `fns`.

        Args:
            other: The argument to pass to each function.

        Returns:
            The result of calling each function in `fns` with `other`.
        """
        return self.__call__(other)
