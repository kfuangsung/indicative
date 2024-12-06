from typing import Any, Iterable


class IndicatorMixin:
    def __call__(self, *args, **kwargs) -> Any:
        return self.compute(*args, **kwargs)

    def __ror__(self, other: Iterable):
        return self(other)


class AdapterMixin:
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class SelectMixin[T]:
    def __call__(self, *args, **kwargs):
        return self.select(*args, **kwargs)

    def __ror__(self, other: Iterable[T]) -> Any:
        return self.select(other)
