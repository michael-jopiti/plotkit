"""Axis styling."""

from __future__ import annotations

from dataclasses import dataclass

from matplotlib.axes import Axes


def with_unit(name: str, unit: str | None = None) -> str:
    """Join a quantity and its unit, e.g. ``with_unit("Time", "s") == "Time (s)"``."""
    return f"{name} ({unit})" if unit else name


def format_label(text: str, upper: bool = False) -> str:
    """Uppercase the quantity name, never the ``(unit)``: ``"Time (s)"`` becomes ``"TIME (s)"``."""
    if not upper:
        return text
    name, sep, unit = text.partition(" (")
    return name.upper() + sep + unit


@dataclass
class AxisFormatter:
    """Clean axes: no top/right spines, outward ticks, labels with units, optional grid."""

    xlabel: str | None = None
    ylabel: str | None = None
    xunit: str | None = None
    yunit: str | None = None
    grid: bool = False
    upper: bool = False

    def apply(self, ax: Axes) -> None:
        """Style ``ax`` in place."""
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(direction="out")
        ax.grid(self.grid)
        if self.xlabel is not None:
            ax.set_xlabel(format_label(with_unit(self.xlabel, self.xunit), self.upper))
        if self.ylabel is not None:
            ax.set_ylabel(format_label(with_unit(self.ylabel, self.yunit), self.upper))
