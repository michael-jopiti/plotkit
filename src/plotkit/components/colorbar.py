"""Colorbar styling."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar


def add_colorbar(ax: Axes, mappable: ScalarMappable, label: str | None = None) -> Colorbar:
    """Add a slim colorbar (about 4% of axes width) with outward ticks and spine-weight outline."""
    cbar = ax.figure.colorbar(mappable, ax=ax, fraction=0.045, pad=0.03, aspect=24, label=label)
    cbar.outline.set_linewidth(ax.spines["left"].get_linewidth())
    cbar.ax.tick_params(direction="out")
    return cbar
