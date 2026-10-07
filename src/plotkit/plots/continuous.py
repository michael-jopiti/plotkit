"""Distribution of a continuous variable: gradient-coloured histogram plus fitted density."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from plotkit.components.marginals import kde
from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot


@register_plot("continuous")
class ContinuousPlot(BasePlot):
    """Histogram of ``data`` (1-D, or column ``x_name`` of a table), colored by density.

    Options: ``bins=40``, ``fit="kde"`` (``"kde"``, ``"normal"`` or ``None``).
    """

    defaults = {"bins": 40, "fit": "kde"}

    def prepare_data(self) -> np.ndarray:
        """Finite values as a float array."""
        x = np.asarray(DataAdapter.vector(self.data, self.xcol).to_numpy(dtype=float))
        x = x[np.isfinite(x)]
        if len(x) < 2:
            raise DataError("continuous() needs at least 2 finite values")
        self.y_name = self.y_name or "Density"
        return x

    def draw(self, ax: Axes, x: np.ndarray) -> None:
        """Histogram bars colored by height, plus the fitted curve."""
        v, fit = self.v, self.opt["fit"]
        cmap = v.continuous().cmap
        ax.plot([], [], "s", ms=5, color=cmap(0.55), label=f"Samples (n={len(x)})")
        heights, edges = np.histogram(x, bins=self.opt["bins"], density=True)
        bars = ax.bar(edges[:-1], heights, np.diff(edges), align="edge")
        for b, h in zip(bars, heights, strict=True):
            b.set_facecolor(cmap(0.1 + 0.8 * h / heights.max()))
            b.set_edgecolor("none")
        if fit is None:
            return
        pad = 0.15 * np.ptp(x)
        grid = np.linspace(x.min() - pad, x.max() + pad, 300)
        if fit == "normal":
            mu, sd = x.mean(), x.std(ddof=1)
            dens = np.exp(-0.5 * ((grid - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
            label = rf"Normal fit ($\mu$={mu:.2g}, $\sigma$={sd:.2g})"
        elif fit == "kde":
            dens, label = kde(x, grid), "Kernel density"
        else:
            raise DataError(f"fit must be 'kde', 'normal' or None, got {fit!r}")
        ax.plot(grid, dens, color=v.fg, lw=1.2, ls="--", label=label)

    def finalize(self, ax: Axes) -> None:
        """Start the density axis at zero."""
        ax.set_ylim(bottom=0)
