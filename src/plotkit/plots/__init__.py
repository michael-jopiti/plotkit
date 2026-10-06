"""Plot classes. Importing this package registers the built-in plots."""

from plotkit.plots import (  # noqa: F401  (registration side effects)
    bar,
    boxplot,
    continuous,
    dim_red,
    heatmap,
    line,
    scatter,
    survival,
    volcano,
)
from plotkit.plots.base import BasePlot, PlotResult
from plotkit.plots.registry import plots, register_plot

__all__ = ["BasePlot", "PlotResult", "plots", "register_plot"]
