"""plotkit: publication-ready scientific figures in one call.

>>> import plotkit
>>> data = plotkit.synthetic.gaussian(2, 0.5)
>>> plotkit.continuous("Value (a.u.)", "Density", "Gaussian distribution", data).save("fig")
"""

from importlib.metadata import PackageNotFoundError, version

from plotkit import synthetic
from plotkit.api import (
    bar,
    boxplot,
    continuous,
    dim_red,
    heatmap,
    line,
    plot,
    scatter,
    survival,
    volcano,
)
from plotkit.exceptions import (
    DataError,
    PaletteError,
    PlotkitError,
    RegistryError,
    ThemeError,
)
from plotkit.io import save_figure
from plotkit.plots import BasePlot, PlotResult, register_plot
from plotkit.themes import Variant, register_variant

try:
    __version__ = version("plotkit")
except PackageNotFoundError:  # running from an uninstalled source tree
    __version__ = "0+unknown"

__all__ = [
    "BasePlot",
    "DataError",
    "PaletteError",
    "PlotResult",
    "PlotkitError",
    "RegistryError",
    "ThemeError",
    "Variant",
    "bar",
    "boxplot",
    "continuous",
    "dim_red",
    "heatmap",
    "line",
    "plot",
    "register_plot",
    "register_variant",
    "save_figure",
    "scatter",
    "survival",
    "synthetic",
    "volcano",
]
