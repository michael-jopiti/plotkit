"""Marginal densities for joint plots: one KDE per group above and beside the main axes."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from matplotlib.axes import Axes

from plotkit.exceptions import DataError

_SIZE = 0.2  # marginal thickness as a fraction of the main axes
_FILL_ALPHA = 0.25


def kde(x: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Gaussian kernel density with Silverman's bandwidth (subsampled above 20 000 points)."""
    if len(x) > 20_000:
        x = np.random.default_rng(0).choice(x, 20_000, replace=False)
    q75, q25 = np.percentile(x, [75, 25])
    h = 0.9 * min(x.std(ddof=1), (q75 - q25) / 1.34 or x.std(ddof=1)) * len(x) ** -0.2
    z = (grid[:, None] - x[None, :]) / h
    dens: np.ndarray = np.exp(-0.5 * z**2).sum(1) / (len(x) * h * np.sqrt(2 * np.pi))
    return dens


def add_marginals(
    ax: Axes,
    groups: Sequence[tuple[str, np.ndarray, np.ndarray]],
    line_width: float,
    bg: str,
) -> Axes:
    """Split ``ax`` into a joint layout and draw one KDE per group on each margin.

    ``groups`` holds ``(color, x, y)`` per label. The marginals share the main axes' limits
    and sit in the same constrained-layout grid, so they align with the data area and cannot
    overlap its ticks or labels. Their grid spans exactly the data range, so they never
    change the shared limits. Returns the top marginal, which carries the title.
    """
    spec = ax.get_subplotspec()
    if spec is None:
        raise DataError("marginals need axes created by subplots() / add_subplot()")
    fig = ax.figure
    gs = spec.subgridspec(
        2, 2, width_ratios=[1, _SIZE], height_ratios=[_SIZE, 1], wspace=0, hspace=0
    )
    ax.set_subplotspec(gs[1, 0])
    top = fig.add_subplot(gs[0, 0], sharex=ax)
    right = fig.add_subplot(gs[1, 1], sharey=ax)
    for color, x, y in groups:
        for vals, side in ((x, top), (y, right)):
            vals = vals[np.isfinite(vals)]
            if len(vals) < 2 or np.ptp(vals) == 0:
                continue
            grid = np.linspace(vals.min(), vals.max(), 200)
            dens = kde(vals, grid)
            if side is top:
                side.fill_between(grid, dens, color=color, alpha=_FILL_ALPHA, lw=0)
                side.plot(grid, dens, color=color, lw=line_width)
            else:
                side.fill_betweenx(grid, dens, color=color, alpha=_FILL_ALPHA, lw=0)
                side.plot(dens, grid, color=color, lw=line_width)
    top.set_ylim(bottom=0)
    right.set_xlim(left=0)
    for m in (top, right):
        m.set_axis_off()
        m.set_facecolor(bg)
    return top
