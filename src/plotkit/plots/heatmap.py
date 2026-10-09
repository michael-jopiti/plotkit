"""Heatmap of a samples-by-features table."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.image import AxesImage

from plotkit.components import add_colorbar, format_label
from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot


@register_plot("heatmap")
class HeatmapPlot(BasePlot):
    """Matrix colored with the continuous gradient.

    ``data`` is a wide table: one row per feature, one numeric column per sample. A leading
    text column (or a pandas index) gives row labels. Options: ``zscore=True`` (standardize
    each row, color range -2..2), ``cbar_label=None``, ``vmin=None`` / ``vmax=None`` (fixed
    color range; override the z-score range too), ``annotate=False`` (print each cell value).
    """

    defaults = {
        "zscore": True,
        "cbar_label": None,
        "vmin": None,
        "vmax": None,
        "annotate": False,
    }

    def prepare_data(self) -> pd.DataFrame:
        """Numeric table indexed by row label."""
        frame = DataAdapter.to_frame(self.data)
        first = frame.columns[0]
        if not pd.api.types.is_numeric_dtype(frame[first]):
            frame = frame.set_index(first)
        num = frame.select_dtypes("number")
        if num.shape != frame.shape or num.empty:
            raise DataError(
                "heatmap() needs a numeric table (plus an optional leading label column)"
            )
        return num

    def figsize(self, prepared: pd.DataFrame) -> tuple[float, float]:
        """Height follows the number of rows."""
        if isinstance(self.size, tuple) or self.aspect_override:
            return super().figsize(prepared)
        w = super().figsize(prepared)[0]
        return (w, float(np.clip(0.22 * len(prepared) + 1.3, 2.4, 7.0)))

    def draw(self, ax: Axes, m: pd.DataFrame) -> None:
        """Cells, tick labels and colorbar."""
        z = m.to_numpy(dtype=float)
        if self.opt["zscore"]:
            sd = z.std(1, keepdims=True)
            z = (z - z.mean(1, keepdims=True)) / np.where(sd > 0, sd, 1.0)  # constant row -> 0
        vmin, vmax = (-2.0, 2.0) if self.opt["zscore"] else (None, None)
        vmin = self.opt["vmin"] if self.opt["vmin"] is not None else vmin
        vmax = self.opt["vmax"] if self.opt["vmax"] is not None else vmax
        cmap = self.v.continuous().cmap
        im = ax.imshow(z, cmap=cmap, aspect="auto", interpolation="nearest", vmin=vmin, vmax=vmax)
        if self.opt["annotate"]:
            self._annotate(ax, im, z)
        ax.set_yticks(range(len(m)), [str(i) for i in m.index])
        if m.shape[1] <= 30:
            ax.set_xticks(range(m.shape[1]), [str(c) for c in m.columns], rotation=90)
        else:
            ax.set_xticks([])
        ax.tick_params(length=0)
        for side in ax.spines.values():
            side.set_visible(False)
        label = self.opt["cbar_label"] or ("z-score" if self.opt["zscore"] else "value")
        add_colorbar(ax, im, format_label(label, self.v.upper_labels))

    def _annotate(self, ax: Axes, im: AxesImage, z: np.ndarray) -> None:
        """Write each finite value in the cell, ink or page colour by cell lightness."""
        for (i, j), val in np.ndenumerate(z):
            if not np.isfinite(val):
                continue
            r, g, b, _ = im.cmap(im.norm(val))
            dark = 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5
            ax.text(
                j,
                i,
                f"{val:.2g}",
                ha="center",
                va="center",
                color=self.v.bg if dark else self.v.fg,
                fontsize=self.v.fontsize - 1,
            )

    def style_legend(self, ax: Axes) -> None:
        """Skip the legend: the colorbar is the key."""
