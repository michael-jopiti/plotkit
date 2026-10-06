"""Theme registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import overload

from plotkit.registry import Registry
from plotkit.themes.base import Theme
from plotkit.themes.publication import PublicationTheme

ThemeFactory = Callable[[], Theme]

themes: Registry[ThemeFactory] = Registry("theme", "plotkit.themes")


@overload
def register_theme(name: str, factory: ThemeFactory, *, overwrite: bool = ...) -> ThemeFactory: ...
@overload
def register_theme(
    name: str, factory: None = ..., *, overwrite: bool = ...
) -> Callable[[ThemeFactory], ThemeFactory]: ...
def register_theme(
    name: str, factory: ThemeFactory | None = None, *, overwrite: bool = False
) -> ThemeFactory | Callable[[ThemeFactory], ThemeFactory]:
    """Register a theme factory ``() -> Theme``; usable as a decorator."""
    if factory is None:
        return lambda f: themes.register(name, f, overwrite=overwrite)
    return themes.register(name, factory, overwrite=overwrite)


def get_theme(name: str = "publication") -> Theme:
    """Build the theme registered as ``name``."""
    return themes.get(name)()


register_theme("publication", PublicationTheme)
