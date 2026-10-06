"""Reusable styling components shared by every plot."""

from plotkit.components.axes import AxisFormatter, with_unit
from plotkit.components.colorbar import add_colorbar
from plotkit.components.layout import Obstacles, text_overlaps
from plotkit.components.legend import LegendStyler
from plotkit.components.size import DOUBLE_COLUMN, GOLDEN, SINGLE_COLUMN, SQUARE, SizePreset
from plotkit.components.title import TitleFormatter

__all__ = [
    "DOUBLE_COLUMN",
    "GOLDEN",
    "SINGLE_COLUMN",
    "SQUARE",
    "AxisFormatter",
    "Obstacles",
    "add_colorbar",
    "text_overlaps",
    "LegendStyler",
    "SizePreset",
    "TitleFormatter",
    "with_unit",
]
