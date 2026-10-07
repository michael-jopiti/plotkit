"""Scatter plot: categorical ``hue`` (colors + marker shapes) or continuous ``color`` (gradient)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from plotkit.components import add_colorbar, add_marginals, format_label
from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot

MARKERS = ("o", "s", "^", "D", "v")


def add_alpha(d: pd.DataFrame, alpha: Any, source: Any = None) -> pd.DataFrame:
    """Add a per-point ``alpha`` column to ``d`` (columns ``x``, ``y``, ...); no-op for ``None``.

    ``alpha`` is a number, a column name in ``source``, an array-like (one value per point) or
    a callable ``f(x, y) -> array`` of the plotted coordinates.
    """
    if alpha is None:
        return d
    if callable(alpha):
        vals: Any = alpha(d["x"].to_numpy(), d["y"].to_numpy())
    elif isinstance(alpha, (int, float)):
        vals = alpha
    else:
        vals = DataAdapter.normalize(source, alpha=alpha).frame["alpha"].to_numpy()
    vals = np.asarray(vals, dtype=float)
    if vals.ndim and len(vals) != len(d):
        raise DataError(f"alpha has {len(vals)} values for {len(d)} points")
    d["alpha"] = np.broadcast_to(vals, len(d))
    return d


def point_alpha(sub: pd.DataFrame) -> Any:
    """Alpha values of the rows in ``sub`` (``None`` when no alpha was requested)."""
    return sub["alpha"].to_numpy() if "alpha" in sub else None


def joint_marginals(ax: Axes, d: pd.DataFrame, v: Any) -> Axes:
    """Add per-``hue`` KDE marginals (one group when ``d`` has no hue) to ``ax``."""
    if "hue" in d:
        levels = list(dict.fromkeys(d["hue"]))
        colors = v.categorical(len(levels)).colors
        groups = [
            (
                c,
                d.loc[d["hue"] == lvl, "x"].to_numpy(float),
                d.loc[d["hue"] == lvl, "y"].to_numpy(float),
            )
            for lvl, c in zip(levels, colors, strict=False)
        ]
    else:
        groups = [(v.categorical(1).colors[0], d["x"].to_numpy(float), d["y"].to_numpy(float))]
    return add_marginals(ax, groups, v.hairline * 2, v.bg)


@register_plot("scatter")
class ScatterPlot(BasePlot):
    """Points at (``x_name``, ``y_name``) columns.

    Options: ``hue=None`` (category column), ``color=None`` (numeric column, gradient +
    colorbar), ``s=14`` (marker area), ``alpha=None`` (opacity in [0, 1]: a number, a column
    name, an array with one value per point, or a callable ``f(x, y) -> array``),
    ``marginals=False`` (``True``: a KDE per ``hue`` level above and beside the axes).
    """

    defaults = {"hue": None, "color": None, "s": 14, "alpha": None, "marginals": False}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``x``, ``y`` and optionally ``hue`` / ``color``."""
        d = DataAdapter.normalize(
            self.data, x=self.xcol, y=self.ycol, hue=self.opt["hue"], color=self.opt["color"]
        ).frame
        return add_alpha(d, self.opt["alpha"], self.data)

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """Scatter marks."""
        v, s, bg = self.v, self.opt["s"], self.v.bg
        if self.opt["marginals"]:
            self.top = joint_marginals(ax, d, v)
        if "color" in d:
            sc = ax.scatter(
                d["x"],
                d["y"],
                c=d["color"],
                cmap=v.continuous().cmap,
                s=s,
                linewidths=0,
                alpha=point_alpha(d),
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
                    alpha=point_alpha(sub),
                )
        else:
            ax.scatter(
                d["x"],
                d["y"],
                s=s,
                color=v.categorical(1).colors[0],
                edgecolors=bg,
                linewidths=0.3,
                alpha=point_alpha(d),
            )
