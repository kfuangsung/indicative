from collections.abc import Callable
from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class NamedTupleProtocol(Protocol):
    """Protocol for named tuples.

    This protocol defines the methods that a named tuple must implement.

    Attributes:
        _make: A class method that creates a new instance of the named tuple.
        _asdict: A method that returns a dictionary representation of the named tuple.
        _replace: A method that returns a new instance of the named tuple with the given
            keyword arguments.
    """

    @classmethod
    def _make(cls): ...

    def _asdict(self) -> dict: ...

    def _replace(**kwargs): ...


@runtime_checkable
class IndicatorProtocol(Protocol):
    """Protocol for indicators.

    This protocol defines the methods that an indicator must implement.

    Attributes:
        compute: A method that computes the indicator.
    """

    def compute(self): ...


@runtime_checkable
class AdapterProtocol(Protocol):
    """Protocol for adapters.

    This protocol defines the methods that an adapter must implement.

    Attributes:
        func: A class variable that is a callable that takes one argument and returns
            one argument.
    """

    func: ClassVar[Callable[[Any], Any]]
