"""Scatter plot: categorical ``hue`` (colors + marker shapes) or continuous ``color`` (gradient)."""

from __future__ import annotations

import pandas as pd
from matplotlib.axes import Axes

from plotkit.components import add_colorbar, format_label
from plotkit.data import DataAdapter
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot

MARKERS = ("o", "s", "^", "D", "v")


@register_plot("scatter")
class ScatterPlot(BasePlot):
    """Points at (``x_name``, ``y_name``) columns.

    Options: ``hue=None`` (category column), ``color=None`` (numeric column, gradient +
    colorbar), ``s=14`` (marker area).
    """

    defaults = {"hue": None, "color": None, "s": 14}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``x``, ``y`` and optionally ``hue`` / ``color``."""
        return DataAdapter.normalize(
            self.data, x=self.xcol, y=self.ycol, hue=self.opt["hue"], color=self.opt["color"]
        ).frame

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """Scatter marks."""
        v, s, bg = self.v, self.opt["s"], self.v.bg
        if "color" in d:
            sc = ax.scatter(
                d["x"], d["y"], c=d["color"], cmap=v.continuous().cmap, s=s, linewidths=0
            )
            add_colorbar(ax, sc, format_label(self.opt["color"], v.upper_labels))
        elif "hue" in d:
            levels = list(dict.fromkeys(d["hue"]))
            pal = v.categorical(len(levels))
            for lvl, color, m in zip(levels, pal.colors, MARKERS, strict=False):
                sub = d[d["hue"] == lvl]
                ax.scatter(
                    sub["x"],
                    sub["y"],
                    s=s,
                    color=color,
                    marker=m,
                    edgecolors=bg,
                    linewidths=0.3,
                    label=str(lvl),
                )
        else:
            ax.scatter(
                d["x"], d["y"], s=s, color=v.categorical(1).colors[0], edgecolors=bg, linewidths=0.3
            )
