"""Palette registry. Factories take an optional size ``n`` and return a Palette."""

from __future__ import annotations

from collections.abc import Callable
from typing import overload

from plotkit.palettes.base import Palette
from plotkit.palettes.categorical import CategoricalPalette
from plotkit.palettes.continuous import ContinuousPalette
from plotkit.palettes.discrete import DiscretePalette
from plotkit.registry import Registry

PaletteFactory = Callable[[int | None], Palette]

palettes: Registry[PaletteFactory] = Registry("palette", "plotkit.palettes")


@overload
def register_palette(
    name: str, factory: PaletteFactory, *, overwrite: bool = ...
) -> PaletteFactory: ...
@overload
def register_palette(
    name: str, factory: None = ..., *, overwrite: bool = ...
) -> Callable[[PaletteFactory], PaletteFactory]: ...
def register_palette(
    name: str, factory: PaletteFactory | None = None, *, overwrite: bool = False
) -> PaletteFactory | Callable[[PaletteFactory], PaletteFactory]:
    """Register a palette factory ``(n | None) -> Palette``; usable as a decorator."""
    if factory is None:
        return lambda f: palettes.register(name, f, overwrite=overwrite)
    return palettes.register(name, factory, overwrite=overwrite)


def get_palette(name: str, n: int | None = None) -> Palette:
    """Build the palette registered as ``name`` with ``n`` colors (if it takes a size)."""
    return palettes.get(name)(n)


register_palette("continuous", lambda n: ContinuousPalette("cividis"))
register_palette("viridis", lambda n: ContinuousPalette("viridis"))
register_palette("discrete", lambda n: DiscretePalette(5 if n is None else n))
register_palette("categorical", lambda n: CategoricalPalette(8 if n is None else n))
