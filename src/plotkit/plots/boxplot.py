"""Boxplot of quantiles per group."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from matplotlib.axes import Axes

from plotkit.data import DataAdapter
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot


@register_plot("boxplot")
class BoxPlot(BasePlot):
    """One box per group.

    ``data`` is a table with a group column ``x_name`` and a value column ``y_name``, or a
    mapping ``{group: values}``. Options: ``order=None`` (group order), ``points=False``
    (overlay the raw values).
    """

    defaults = {"order": None, "points": False}

    def prepare_data(self) -> dict[str, np.ndarray]:
        """Values per group, in first-seen (or ``order``) order."""
        if isinstance(self.data, Mapping) and self.xcol not in self.data:
            groups = {str(k): np.asarray(vals, dtype=float) for k, vals in self.data.items()}
        else:
            d = DataAdapter.normalize(self.data, x=self.xcol, y=self.ycol).frame
            groups = {str(k): g["y"].to_numpy(dtype=float) for k, g in d.groupby("x", sort=False)}
        order = self.opt["order"] or list(groups)
        return {str(k): groups[str(k)] for k in order}

    def draw(self, ax: Axes, groups: dict[str, np.ndarray]) -> None:
        """Boxes in categorical colors, medians in ink."""
        v, lw = self.v, self.v.hairline
        pal = v.categorical(len(groups))
        bp = ax.boxplot(
            list(groups.values()),
            tick_labels=list(groups),
            patch_artist=True,
            widths=0.55,
            flierprops={
                "marker": "o",
                "markersize": 2.5,
                "markeredgewidth": lw,
                "markeredgecolor": v.fg,
            },
            medianprops={"color": v.fg, "linewidth": 2.5 * lw},
            boxprops={"linewidth": lw, "edgecolor": v.fg},
            whiskerprops={"linewidth": lw, "color": v.fg},
            capprops={"linewidth": lw, "color": v.fg},
            showfliers=not self.opt["points"],
        )
        for patch, color in zip(bp["boxes"], pal.colors, strict=True):
            patch.set_facecolor(color)
        if self.opt["points"]:
            rng = np.random.default_rng(0)
            for i, vals in enumerate(groups.values(), start=1):
                ax.scatter(
                    i + rng.uniform(-0.15, 0.15, len(vals)),
                    vals,
                    s=4,
                    color=v.fg,
                    linewidths=0,
                    zorder=3,
                )

    def style_legend(self, ax: Axes) -> None:
        """Skip the legend: groups are labelled on the axis."""
