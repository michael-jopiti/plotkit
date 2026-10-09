"""Reusable styling components shared by every plot."""

from plotkit.components.axes import AxisFormatter, format_label, with_unit
from plotkit.components.colorbar import add_colorbar
from plotkit.components.layout import Obstacles, text_overlaps
from plotkit.components.legend import LegendStyler
from plotkit.components.marginals import add_marginals
from plotkit.components.size import DOUBLE_COLUMN, GOLDEN, SINGLE_COLUMN, SQUARE, SizePreset
from plotkit.components.title import TitleFormatter, add_caption, add_panel_caption

__all__ = [
    "DOUBLE_COLUMN",
    "GOLDEN",
    "SINGLE_COLUMN",
    "SQUARE",
    "AxisFormatter",
    "Obstacles",
    "add_caption",
    "add_panel_caption",
    "add_marginals",
    "add_colorbar",
    "text_overlaps",
    "LegendStyler",
    "SizePreset",
    "TitleFormatter",
    "format_label",
    "with_unit",
]
