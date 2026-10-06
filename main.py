"""Smoke test: one figure per palette type (continuous, discrete, categorical)."""

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib.figure import Figure

from plotkit.components import (
    SINGLE_COLUMN,
    AxisFormatter,
    LegendStyler,
    TitleFormatter,
    add_colorbar,
    text_overlaps,
)
from plotkit.io import save_figure
from plotkit.palettes import get_palette
from plotkit.themes import get_theme

rng = np.random.default_rng(0)
OUT = "examples/output"


def continuous():
    x, y = rng.uniform(-3, 3, (2, 400))
    z = np.exp(-(x**2 + y**2) / 4) * np.cos(2 * x)
    fig = Figure(figsize=SINGLE_COLUMN.figsize())
    ax = fig.subplots()
    sc = ax.scatter(x, y, c=z, cmap=get_palette("continuous").cmap, s=12)
    add_colorbar(ax, sc, r"$f(x, y)$ (a.u.)")
    AxisFormatter("x", "y", "mm", "mm").apply(ax)
    TitleFormatter("Continuous: cividis").apply(ax)
    return fig


def discrete():
    doses = [0.1, 1, 10, 100, 1000]
    pal = get_palette("discrete", len(doses))
    styles = ["-", "--", "-.", ":", (0, (5, 1))]
    t = np.linspace(0, 10, 100)
    fig = Figure(figsize=SINGLE_COLUMN.figsize())
    ax = fig.subplots()
    for dose, color, ls in zip(doses, pal.colors, styles):
        ax.plot(t, 1 - np.exp(-t * dose**0.4 / 10), color=color, ls=ls, label=f"{dose:g}")
    AxisFormatter("Time", "Response", "h", "norm.").apply(ax)
    TitleFormatter("Discrete (ordered): dose").apply(ax)
    LegendStyler(title="Dose (nM)").apply(ax)
    return fig


def categorical():
    groups = ["A", "B", "C", "D"]
    pal = get_palette("categorical", len(groups))
    markers = ["o", "s", "^", "D"]
    fig = Figure(figsize=SINGLE_COLUMN.figsize())
    ax = fig.subplots()
    for i, (g, color, m) in enumerate(zip(groups, pal.colors, markers)):
        x = rng.normal(i * 1.5, 0.7, 30)
        y = rng.normal(i * 0.8, 0.7, 30)
        ax.scatter(x, y, color=color, marker=m, s=14, label=g)
    AxisFormatter("PC1", "PC2").apply(ax)
    TitleFormatter("Categorical: Okabe-Ito").apply(ax)
    LegendStyler(title="Group").apply(ax)
    return fig


with get_theme("publication").context():
    for name, make in [
        ("continuous", continuous),
        ("discrete", discrete),
        ("categorical", categorical),
    ]:
        fig = make()
        print(name, "text overlaps:", text_overlaps(fig))
        save_figure(fig, f"{OUT}/main_{name}")
        print("saved", name)
