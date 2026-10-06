"""Palettes: continuous, discrete (ordered) and categorical (unordered)."""

from plotkit.palettes.base import Palette
from plotkit.palettes.categorical import CategoricalPalette
from plotkit.palettes.continuous import ContinuousPalette
from plotkit.palettes.discrete import DiscretePalette
from plotkit.palettes.registry import get_palette, register_palette

__all__ = [
    "CategoricalPalette",
    "ContinuousPalette",
    "DiscretePalette",
    "Palette",
    "get_palette",
    "register_palette",
]
