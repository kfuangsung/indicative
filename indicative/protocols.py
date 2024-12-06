from typing import Any, Callable, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class NamedTupleProtocol(Protocol):
    @classmethod
    def _make(iterable): ...

    def _asdict() -> dict: ...

    def _replace(**kwargs): ...


@runtime_checkable
class IndicatorProtocol(Protocol):
    def compute(self, *args, **kwargs) -> Any: ...


@runtime_checkable
class AdapterProtocol(Protocol):
    func: ClassVar[Callable[[Any], Any]]
