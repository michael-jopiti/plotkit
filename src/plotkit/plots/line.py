"""Line plot, optionally one line per ``hue`` level."""

from __future__ import annotations

import pandas as pd
from matplotlib.axes import Axes

from plotkit.components import LegendStyler, format_label
from plotkit.data import DataAdapter
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot

STYLES = ("-", "--", "-.", ":", (0, (5, 1)))


@register_plot("line")
class LinePlot(BasePlot):
    """Lines of ``y_name`` against ``x_name``.

    Options: ``hue=None`` (column splitting lines), ``ordered=False`` (hue levels are ordered,
    e.g. doses: use the sequential discrete palette instead of categorical colors),
    ``markers=False``. Line styles differ per level as a non-color cue.
    """

    defaults = {"hue": None, "ordered": False, "markers": False}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``x``, ``y`` and optionally ``hue``, sorted by ``x``."""
        d = DataAdapter.normalize(self.data, x=self.xcol, y=self.ycol, hue=self.opt["hue"]).frame
        return d.sort_values("x", kind="stable")

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """One line per level."""
        v = self.v
        if "hue" not in d:
            ax.plot(
                d["x"],
                d["y"],
                color=v.categorical(1).colors[0],
                marker="o" if self.opt["markers"] else None,
            )
            return
        levels = sorted(d["hue"].unique()) if self.opt["ordered"] else list(dict.fromkeys(d["hue"]))
        n = len(levels)
        pal = v.discrete(n) if self.opt["ordered"] and 3 <= n <= 9 else v.categorical(n)
        for i, (lvl, color) in enumerate(zip(levels, pal.colors, strict=True)):
            sub = d[d["hue"] == lvl]
            ax.plot(
                sub["x"],
                sub["y"],
                color=color,
                ls=STYLES[i % len(STYLES)],
                marker="osv^D"[i % 5] if self.opt["markers"] else None,
                label=f"{lvl:g}" if isinstance(lvl, float) else str(lvl),
            )

    def style_legend(self, ax: Axes) -> None:
        """Legend titled with the hue column."""
        hue = self.opt["hue"]
        LegendStyler(title=hue and format_label(str(hue), self.v.upper_labels)).apply(ax)
