"""Legend styling with automatic, overlap-free placement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.transforms import Bbox

from plotkit.components.layout import Obstacles

_INSIDE = (
    "upper right",
    "upper left",
    "lower right",
    "lower left",
    "center right",
    "center left",
    "lower center",
    "upper center",
)
_GAP_PT = 3.0  # minimum clear distance between legend and data


@dataclass
class LegendStyler:
    """Frameless legend placed where it covers no data.

    Tries every inside position, measuring the legend box against densely
    sampled lines, scatter points, bars and images. If none is clear, the legend
    goes outside, right of the axes.

    Parameters
    ----------
    title
        Legend title.
    auto
        Search for a free position. Otherwise use ``loc``.
    loc
        Matplotlib location used when ``auto`` is false.
    frame
        Draw a thin frame.
    """

    title: str | None = None
    auto: bool = True
    loc: str = "best"
    frame: bool = False

    def apply(self, ax: Axes) -> Legend | None:
        """Create the legend on ``ax``. Return it, or ``None`` when nothing is labelled."""
        handles, labels = ax.get_legend_handles_labels()
        if not handles:
            return None

        def make(loc: str, anchor: tuple[float, float] | None = None) -> Legend:
            leg: Legend = ax.legend(  # type: ignore[call-overload]
                handles,
                labels,
                loc=loc,
                bbox_to_anchor=anchor,
                title=self.title,
                frameon=self.frame,
                alignment="left",
            )
            if self.frame:
                leg.get_frame().set_linewidth(ax.spines["left"].get_linewidth())
            return leg

        if not self.auto:
            return make(self.loc)
        cast(Figure, ax.figure).draw_without_rendering()
        obstacles = Obstacles(ax)
        gap = _GAP_PT * ax.figure.dpi / 72
        for loc in _INSIDE:
            leg = make(loc)
            box = leg.get_window_extent()
            padded = Bbox.from_extents(box.x0 - gap, box.y0 - gap, box.x1 + gap, box.y1 + gap)
            if obstacles.score(padded) == 0:
                return leg
        return make("upper left", (1.02, 1.0))
