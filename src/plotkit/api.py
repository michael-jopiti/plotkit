"""One-call plotting API: ``plotkit.<kind>(x_name, y_name, title, data, **options)``.

Every function returns a :class:`~plotkit.plots.PlotResult` (``.fig``, ``.ax``) and accepts
the common options ``style`` (``"editorial"`` or ``"cobalt"``), ``size`` (``"single"``,
``"double"`` or ``(w, h)`` inches), ``aspect``, ``ax`` and ``save`` (path without suffix; writes
PDF, SVG and PNG). ``data`` may be a pandas or polars table. Axis labels may carry units:
``"Time (s)"``.
"""

from __future__ import annotations

from typing import Any

from plotkit.plots import PlotResult, plots


def plot(
    kind: str, x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Draw the registered plot ``kind``; the entry point for custom (registered) plots."""
    return plots.get(kind)(x_name, y_name, title, data, **options).render()


def continuous(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Distribution of a continuous variable: histogram colored by density plus a fitted curve.

    ``data``: 1-D values, or a table (then ``x_name`` is the column).
    Options: ``bins=40``, ``fit="kde"|"normal"|None``.
    """
    return plot("continuous", x_name, y_name, title, data, **options)


def boxplot(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Quantile boxes per group.

    ``data``: table with group column ``x_name`` and value column ``y_name``,
    or ``{group: values}``.
    Options: ``order=None``, ``points=False``.
    """
    return plot("boxplot", x_name, y_name, title, data, **options)


def bar(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Mean per category with error bars and replicate points, optionally split by ``hue``.

    ``data``: table with category column ``x_name`` and value column ``y_name``.
    Options: ``hue=None``, ``error="sd"|"sem"|None``, ``points=True``.
    """
    return plot("bar", x_name, y_name, title, data, **options)


def scatter(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Scatter of columns ``x_name`` and ``y_name``.

    Options: ``hue=None`` (category column), ``color=None`` (numeric column, gradient), ``s=14``,
    ``alpha=None`` (number, column name, per-point array, or ``f(x, y) -> array``).
    """
    return plot("scatter", x_name, y_name, title, data, **options)


def line(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Lines of column ``y_name`` against ``x_name``, one per ``hue`` level.

    Options: ``hue=None``, ``ordered=False`` (ordinal hue such as dose), ``markers=False``.
    """
    return plot("line", x_name, y_name, title, data, **options)


def dim_red(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """PCA / UMAP / precomputed embedding scatter.

    ``method=None``: ``data`` has coordinate columns ``x_name`` and ``y_name``.
    ``method="pca"|"umap"``: ``data`` has feature columns and the embedding is computed for you.
    Options: ``hue=None``, ``method=None``, ``n_neighbors=15``, ``min_dist=0.3``,
    ``seed=0``, ``s=10``, ``alpha=None`` (number, column name, per-point array, or
    ``f(x, y) -> array`` of the embedding coordinates).
    """
    return plot("dim_red", x_name, y_name, title, data, **options)


def survival(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Kaplan-Meier curves.

    ``data``: table with time, event (1 = event, 0 = censored) and group columns.
    Options: ``time="time"``, ``event="event"``, ``group="group"``.
    """
    return plot("survival", x_name, y_name, title, data, **options)


def volcano(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Volcano plot of differential expression.

    ``data``: table with log2 fold change and p-value columns.
    Options: ``lfc="log2fc"``, ``p="pvalue"``, ``lfc_cut=1.0``, ``p_cut=0.01``.
    """
    return plot("volcano", x_name, y_name, title, data, **options)


def heatmap(
    x_name: str | None, y_name: str | None, title: str | None, data: Any, **options: Any
) -> PlotResult:
    """Heatmap of a wide table (rows = features, columns = samples, optional label column).

    Options: ``zscore=True``, ``cbar_label=None``.
    """
    return plot("heatmap", x_name, y_name, title, data, **options)
