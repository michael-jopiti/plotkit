"""Generic name -> object registry with optional entry-point discovery."""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Generic, TypeVar

from plotkit.exceptions import RegistryError

T = TypeVar("T")


class Registry(Generic[T]):
    """Map names to objects. Unknown names fall back to entry points.

    Parameters
    ----------
    kind
        Human-readable kind, used in error messages (e.g. ``"palette"``).
    group
        Entry-point group scanned on first lookup miss (e.g. ``"plotkit.palettes"``).
    """

    def __init__(self, kind: str, group: str) -> None:
        self.kind = kind
        self.group = group
        self._items: dict[str, T] = {}
        self._scanned = False

    def register(self, name: str, obj: T, *, overwrite: bool = False) -> T:
        """Register ``obj`` under ``name``. Raise if taken unless ``overwrite``."""
        if name in self._items and not overwrite:
            raise RegistryError(f"{self.kind} {name!r} already registered")
        self._items[name] = obj
        return obj

    def get(self, name: str) -> T:
        """Return the object registered as ``name``."""
        if name not in self._items:
            self._scan()
        try:
            return self._items[name]
        except KeyError:
            raise RegistryError(
                f"unknown {self.kind} {name!r}; available: {self.names()}"
            ) from None

    def names(self) -> list[str]:
        """Sorted registered names."""
        self._scan()
        return sorted(self._items)

    def _scan(self) -> None:
        if self._scanned:
            return
        self._scanned = True
        for ep in entry_points(group=self.group):
            self._items.setdefault(ep.name, ep.load())
