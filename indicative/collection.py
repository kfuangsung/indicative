from typing import Any, Callable

from pydantic.dataclasses import dataclass


@dataclass
class Collection:
    fns: tuple[Callable[[Any], Any], ...]

    def __call__(self, *args, **kwargs):
        return [f(*args, **kwargs) for f in self.fns]

    def __ror__(self, other: Any) -> Any:
        return self.__call__(other)
