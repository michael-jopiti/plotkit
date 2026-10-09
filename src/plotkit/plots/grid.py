"""Matrix of plots with per-panel and figure-level title, subtitle and caption."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from plotkit.components import DOUBLE_COLUMN, SINGLE_COLUMN, add_caption
from plotkit.components.title import _height_pt
from plotkit.plots.base import PlotResult
from plotkit.plots.registry import plots
from plotkit.themes.styled import Variant, get_variant

_FIGURE_WIDE = {"style", "size", "aspect", "ax", "save"}  # one value for the whole figure


class Panel:
    """One cell of a :func:`grid`: the arguments of ``plotkit.<kind>(...)``.

    Parameters
    ----------
    kind
        Registered plot name, e.g. ``"scatter"``.
    x_name, y_name, title, data
        As in the plot functions.
    **options
        Plot options, including this panel's ``subtitle`` and ``caption``. ``style``,
        ``size``, ``aspect``, ``ax`` and ``save`` belong to the figure: pass them to
        :func:`grid`.
    """

    def __init__(
        self,
        kind: str,
        x_name: str | None,
        y_name: str | None,
        title: str | None,
        data: Any,
        **options: Any,
    ) -> None:
        clash = _FIGURE_WIDE & set(options)
        if clash:
            raise TypeError(
                f"Panel() got figure-wide option(s) {sorted(clash)}; pass them to grid()"
            )
        self.kind, self.args, self.options = kind, (x_name, y_name, title, data), options


@dataclass
class GridResult(PlotResult):
    """:class:`PlotResult` of a grid: ``ax`` is the first panel, ``axes`` the whole matrix."""

    axes: np.ndarray = field(default_factory=lambda: np.empty((0, 0), dtype=object))


def render_grid(
    panels: Sequence[Sequence[Panel | None]],
    title: str | None,
    subtitle: str | None,
    caption: str | None,
    style: str | Variant,
    size: str | tuple[float, float],
    aspect: float,
) -> GridResult:
    """Draw ``panels`` (a list of equal-length rows; ``None`` leaves a cell empty)."""
    nrows, ncols = len(panels), len(panels[0]) if panels else 0
    if not nrows or not ncols or any(len(row) != ncols for row in panels):
        raise ValueError("panels must be a non-empty list of rows with the same length")
    if isinstance(size, str) and size not in ("single", "double"):
        raise ValueError(f"size must be 'single', 'double' or (w, h); got {size!r}")
    v = get_variant(style)
    theme = v.theme()
    props, rc = theme.proportions, theme.rc_params()
    with mpl.rc_context(rc):  # type: ignore[arg-type]
        if isinstance(size, tuple):
            width, height = size
        else:
            width = (DOUBLE_COLUMN if size == "double" else SINGLE_COLUMN).width
            height = nrows * width / ncols / aspect
        fig = Figure(figsize=(width, height))
        pad = props.layout_pad
        head: list[tuple[str, float, str, str]] = []  # title, then subtitle
        if title:
            head.append((title, round(v.title_size * 1.25 * 2) / 2, "bold", v.fg))
        if subtitle:
            head.append((subtitle, props.subtitle, "normal", v.muted))
        texts = [
            fig.text(pad / width, 1.0, t, ha="left", va="top", fontsize=s, fontweight=w, color=c)
            for t, s, w, c in head
        ]
        gap = props.subtitle_gap / 72
        used = pad + sum(_height_pt(t) / 72 + gap for t in texts)  # inches taken at the top
        if texts and not isinstance(size, tuple):
            height += used
            fig.set_size_inches(width, height)
        y = height - pad
        for t in texts:
            t.set_position((pad / width, y / height))
            y -= _height_pt(t) / 72 + gap
        if texts:
            fig.get_layout_engine().set(rect=(0, 0, 1, 1 - used / height))  # type: ignore[union-attr, call-arg]
        axes = fig.subplots(nrows, ncols, squeeze=False)
        cell_pt = width * 72 / ncols * 0.7
        for row, axrow in zip(panels, axes, strict=True):
            for panel, ax in zip(row, axrow, strict=True):
                if panel is None:
                    fig.delaxes(ax)
                    continue
                _draw_panel(panel, ax, v, cell_pt)
        if caption:
            add_caption(fig, caption, props, v.muted)
    first = next(a for a in axes.flat if a in fig.axes)
    return GridResult(fig, first, rc, axes)


def _draw_panel(panel: Panel, ax: Axes, v: Variant, width_pt: float) -> None:
    plot = plots.get(panel.kind)(*panel.args, **panel.options, style=v, ax=ax)
    plot.panel_width_pt = width_pt
    plot.render()
