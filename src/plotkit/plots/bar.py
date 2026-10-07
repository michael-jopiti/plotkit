"""Grouped bars: mean with error bars and the individual observations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot

HATCHES = ("", "////", "\\\\\\\\", "xxxx", "....")


@register_plot("bar")
class BarPlot(BasePlot):
    """Mean per category (``x_name``) of ``y_name``, optionally split by a ``hue`` column.

    Options: ``hue=None``, ``error="sd"`` (``"sd"``, ``"sem"`` or ``None``), ``points=True``.
    Later hue levels get hatching as a second, non-color cue.
    """

    defaults = {"hue": None, "error": "sd", "points": True}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``x``, ``y`` and ``hue`` (constant when no hue)."""
        if self.opt["error"] not in ("sd", "sem", None):
            raise DataError(f"error must be 'sd', 'sem' or None, got {self.opt['error']!r}")
        d = DataAdapter.normalize(self.data, x=self.xcol, y=self.ycol, hue=self.opt["hue"]).frame
        if "hue" not in d:
            d["hue"] = ""
        return d

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """One bar group per category."""
        v, lw = self.v, self.v.hairline
        cats, hues = list(dict.fromkeys(d["x"])), list(dict.fromkeys(d["hue"]))
        pal = v.categorical(len(hues))
        width = 0.72 / len(hues)
        rng = np.random.default_rng(0)
        for i, (hue, color) in enumerate(zip(hues, pal.colors, strict=True)):
            sub = d[d["hue"] == hue]
            g = sub.groupby("x", sort=False)["y"]
            mean = g.mean().reindex(cats)
            err = {"sd": g.std(), "sem": g.sem(), None: None}[self.opt["error"]]
            pos = np.arange(len(cats)) + (i - (len(hues) - 1) / 2) * width
            ax.bar(
                pos,
                mean,
                width,
                yerr=None if err is None else err.reindex(cats),
                color=color,
                edgecolor=v.fg,
                hatch=HATCHES[i % len(HATCHES)],
                linewidth=lw,
                error_kw={"elinewidth": lw, "capsize": 2, "capthick": lw, "ecolor": v.fg},
                label=str(hue) if hue != "" else None,
            )
            if self.opt["points"]:
                for p, c in zip(pos, cats, strict=True):
                    pts = sub.loc[sub["x"] == c, "y"]
                    ax.scatter(
                        p + rng.uniform(-width / 4, width / 4, len(pts)),
                        pts,
                        s=4,
                        color=v.fg,
                        linewidths=0,
                        zorder=3,
                    )
        ax.set_xticks(np.arange(len(cats)), [str(c) for c in cats])
