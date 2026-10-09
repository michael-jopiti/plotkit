"""One-call plotting API: ``plotkit.<kind>(x_name, y_name, title, data, **options)``.

Every function returns a :class:`~plotkit.plots.PlotResult` (``.fig``, ``.ax``). ``data`` may
be a pandas or polars table. Axis labels may carry units (``"Time (s)"``) and are matched to
column names ignoring case, spaces and the unit; use ``x=`` / ``y=`` to name a column
explicitly.

Common keyword options, accepted by every function (:class:`CommonOptions`):

``style``
    ``"editorial"`` (default), ``"cobalt"`` or a :class:`~plotkit.Variant`.
``size``
    ``"single"`` (3.5 in), ``"double"`` (7.2 in) or ``(width, height)`` in inches.
``aspect``
    Width / height; each plot has its own default.
``x``, ``y``
    Column names for x / y when they differ from the axis labels.
``ax``
    Draw into an existing matplotlib axes instead of creating a figure.
``subtitle``, ``caption``
    Optional text under the title / below the figure.
``save``
    Path without suffix; writes a PNG. For other formats or dpi call
    ``result.save(path, formats=..., dpi=...)``.
``xlim``, ``ylim``
    ``(low, high)`` axis limits, e.g. ``ylim=(0.5, 1)`` for a score bounded by 1.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

import numpy as np
from matplotlib.axes import Axes

from plotkit.plots import GridResult, Panel, PlotResult, plots, render_grid
from plotkit.themes import Variant

if TYPE_CHECKING:
    from typing_extensions import Unpack

Alpha = float | str | Sequence[float] | np.ndarray | Callable[[np.ndarray, np.ndarray], Any]
"""Opacity: a number, a column name, one value per point, or ``f(x, y) -> array``."""


class CommonOptions(TypedDict, total=False):
    """Keyword options shared by every plot function."""

    style: str | Variant
    size: str | tuple[float, float]
    aspect: float
    x: str
    y: str
    ax: Axes
    save: str | Path
    xlim: tuple[float, float]
    ylim: tuple[float, float]
    subtitle: str
    caption: str


def plot(
    kind: str,
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    **options: Any,
) -> PlotResult:
    """Draw the registered plot ``kind``; the entry point for custom (registered) plots.

    Parameters
    ----------
    kind
        Name given to :func:`~plotkit.register_plot`, e.g. ``"scatter"``.
    x_name, y_name
        Axis labels (also column names unless ``x=`` / ``y=`` are given).
    title
        Figure title.
    data
        pandas or polars table, array-like or mapping, as the plot requires.
    **options
        Common options (see :mod:`plotkit.api`) and the plot's own options. Unknown names
        raise ``TypeError``.

    Returns
    -------
    PlotResult
    """
    return plots.get(kind)(x_name, y_name, title, data, **options).render()


def grid(
    panels: Sequence[Sequence[Panel | None]],
    title: str | None = None,
    subtitle: str | None = None,
    caption: str | None = None,
    *,
    style: str | Variant = "editorial",
    size: str | tuple[float, float] = "double",
    aspect: float = 4 / 3,
    save: str | Path | None = None,
) -> GridResult:
    """Matrix of plots sharing one style, with a figure title, subtitle and caption.

    Each panel keeps its own title, subtitle and caption (pass them to :class:`Panel`).
    The figure title and subtitle sit above the matrix, the caption below it.

    Parameters
    ----------
    panels
        List of equal-length rows of :class:`Panel`; ``None`` leaves a cell empty.
    title, subtitle, caption
        Figure-level text.
    style
        Registered style name or a :class:`~plotkit.Variant`, used by every panel.
    size
        ``"single"``, ``"double"`` (default) or total ``(width, height)`` in inches. With a
        name, the height follows ``aspect`` per panel plus room for the figure title.
    aspect
        Width / height of one panel.
    save
        Path without suffix; writes a PNG.

    Returns
    -------
    GridResult
        ``.fig``, ``.axes`` (matrix of axes), ``.save()``, ``.overlaps()``.
    """
    result = render_grid(panels, title, subtitle, caption, style, size, aspect)
    if save is not None:
        result.save(save)
    return result


def continuous(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    bins: int = 40,
    fit: Literal["kde", "normal"] | None = "kde",
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Distribution of a continuous variable: histogram colored by density plus a fit.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title. ``y_name`` defaults to ``"Density"``.
    data
        1-D values, or a table (then ``x_name`` / ``x`` names the column).
    bins
        Number of histogram bins.
    fit
        Overlaid curve: kernel density, normal fit, or none.
    **common
        See :class:`CommonOptions`.
    """
    return plot("continuous", x_name, y_name, title, data, bins=bins, fit=fit, **common)


def boxplot(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    order: Sequence[str] | None = None,
    points: bool = False,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Quantile boxes per group.

    Parameters
    ----------
    x_name, y_name, title
        Group-axis label, value-axis label and title.
    data
        Table with group column ``x_name`` and value column ``y_name``, or ``{group: values}``.
    order
        Group order; first-seen order when omitted.
    points
        Overlay the raw values instead of drawing outliers.
    **common
        See :class:`CommonOptions`.
    """
    return plot("boxplot", x_name, y_name, title, data, order=order, points=points, **common)


def bar(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    hue: str | None = None,
    error: Literal["sd", "sem"] | None = "sd",
    points: bool = True,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Mean per category with error bars and replicate points, optionally split by ``hue``.

    Parameters
    ----------
    x_name, y_name, title
        Category-axis label, value-axis label and title.
    data
        Table with category column ``x_name`` and value column ``y_name``.
    hue
        Column splitting each category into grouped bars (later levels are hatched).
    error
        Error-bar statistic: standard deviation, standard error, or none.
    points
        Draw the individual observations.
    **common
        See :class:`CommonOptions`.
    """
    return plot("bar", x_name, y_name, title, data, hue=hue, error=error, points=points, **common)


def scatter(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    hue: str | None = None,
    color: str | None = None,
    s: float = 14,
    alpha: Alpha | None = None,
    marginals: bool = False,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Scatter of columns ``x_name`` and ``y_name``.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title.
    data
        Table with the x and y columns.
    hue
        Categorical column: one color and marker shape per level.
    color
        Numeric column: gradient color with a colorbar.
    s
        Marker area in points squared.
    alpha
        Opacity in [0, 1]: a number, a column name, one value per point, or
        ``f(x, y) -> array``.
    marginals
        Add a KDE per ``hue`` level above and beside the axes.
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "scatter",
        x_name,
        y_name,
        title,
        data,
        hue=hue,
        color=color,
        s=s,
        alpha=alpha,
        marginals=marginals,
        **common,
    )


def line(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    hue: str | None = None,
    ordered: bool = False,
    markers: bool = False,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Lines of column ``y_name`` against ``x_name``, one per ``hue`` level.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title.
    data
        Table with the x and y columns.
    hue
        Column splitting the lines; levels also differ by line style.
    ordered
        The hue levels are ordinal (e.g. dose): use the sequential palette.
    markers
        Draw point markers.
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "line", x_name, y_name, title, data, hue=hue, ordered=ordered, markers=markers, **common
    )


def dim_red(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    hue: str | Sequence[Any] | None = None,
    method: Literal["pca", "umap"] | None = None,
    n_neighbors: int = 15,
    min_dist: float = 0.3,
    seed: int = 0,
    s: float = 10,
    alpha: Alpha | None = None,
    marginals: bool = False,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """PCA / UMAP / precomputed embedding scatter on an equal-scale axes.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title. With ``method="pca"`` the explained variance is appended.
    data
        ``method=None``: coordinate columns ``x_name`` and ``y_name`` (or an ``(n, >=2)``
        array). ``method`` set: a feature table; all numeric columns except ``hue`` are used.
    hue
        Group column. With ``method`` set it must be a column name; otherwise it may also be
        an array of labels.
    method
        Compute the embedding: ``"pca"``, or ``"umap"`` (needs ``plotkit[umap]``).
    n_neighbors, min_dist
        UMAP parameters.
    seed
        Random seed for UMAP and for the draw order.
    s
        Marker area in points squared.
    alpha
        Opacity in [0, 1]: a number, a column name, one value per point, or
        ``f(x, y) -> array`` of the embedding coordinates.
    marginals
        Add a KDE per ``hue`` level above and beside the axes (drops the equal-scale rule).
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "dim_red",
        x_name,
        y_name,
        title,
        data,
        hue=hue,
        method=method,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        seed=seed,
        s=s,
        alpha=alpha,
        marginals=marginals,
        **common,
    )


def survival(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    time: str = "time",
    event: str = "event",
    group: str = "group",
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Kaplan-Meier curves with censoring ticks.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title.
    data
        Table with time, event (1 = event, 0 = censored) and group columns.
    time, event, group
        Column names. A missing default ``group`` column gives one curve; a ``group`` you
        name that does not exist raises ``DataError``.
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "survival", x_name, y_name, title, data, time=time, event=event, group=group, **common
    )


def volcano(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    lfc: str = "log2fc",
    p: str = "pvalue",
    lfc_cut: float = 1.0,
    p_cut: float = 0.01,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Volcano plot of differential expression.

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title.
    data
        Table with log2 fold change and p-value columns.
    lfc, p
        Column names of the log2 fold change and the p-value.
    lfc_cut, p_cut
        Thresholds for calling a point up / down (``|lfc| > lfc_cut`` and ``p < p_cut``).
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "volcano",
        x_name,
        y_name,
        title,
        data,
        lfc=lfc,
        p=p,
        lfc_cut=lfc_cut,
        p_cut=p_cut,
        **common,
    )


def heatmap(
    x_name: str | None,
    y_name: str | None,
    title: str | None,
    data: Any,
    *,
    zscore: bool = True,
    cbar_label: str | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    annotate: bool = False,
    **common: Unpack[CommonOptions],
) -> PlotResult:
    """Heatmap of a wide table (rows = features, columns = samples).

    Parameters
    ----------
    x_name, y_name, title
        Axis labels and title.
    data
        Numeric table, optionally with a leading label column (or a pandas index).
    zscore
        Standardize each row; the color range is then fixed to -2..2.
    cbar_label
        Colorbar label; defaults to ``"z-score"`` or ``"value"``.
    vmin, vmax
        Fixed color range (e.g. 0 and 100 for percentages, -1 and 1 for correlations).
        Overrides the -2..2 z-score range.
    annotate
        Print each cell value inside the cell.
    **common
        See :class:`CommonOptions`.
    """
    return plot(
        "heatmap",
        x_name,
        y_name,
        title,
        data,
        zscore=zscore,
        cbar_label=cbar_label,
        vmin=vmin,
        vmax=vmax,
        annotate=annotate,
        **common,
    )
