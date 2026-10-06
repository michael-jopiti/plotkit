"""Axis styling."""

from __future__ import annotations

from dataclasses import dataclass

from matplotlib.axes import Axes


def with_unit(name: str, unit: str | None = None) -> str:
    """Join a quantity and its unit, e.g. ``with_unit("Time", "s") == "Time (s)"``."""
    return f"{name} ({unit})" if unit else name


@dataclass
class AxisFormatter:
    """Clean axes: no top/right spines, outward ticks, labels with units, optional grid."""

    xlabel: str | None = None
    ylabel: str | None = None
    xunit: str | None = None
    yunit: str | None = None
    grid: bool = False

    def apply(self, ax: Axes) -> None:
        """Style ``ax`` in place."""
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(direction="out")
        ax.grid(self.grid)
        if self.xlabel is not None:
            ax.set_xlabel(with_unit(self.xlabel, self.xunit))
        if self.ylabel is not None:
            ax.set_ylabel(with_unit(self.ylabel, self.yunit))
