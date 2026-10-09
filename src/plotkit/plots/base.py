"""Plot template: prepare_data -> draw -> style_axes -> style_legend -> finalize."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from plotkit.components import (
    DOUBLE_COLUMN,
    SINGLE_COLUMN,
    AxisFormatter,
    LegendStyler,
    TitleFormatter,
    add_caption,
    text_overlaps,
)
from plotkit.io import save_figure
from plotkit.themes.styled import Variant, get_variant

_SIZES = {"single": SINGLE_COLUMN, "double": DOUBLE_COLUMN}


@dataclass
class PlotResult:
    """What every plot returns: keep customizing ``ax`` / ``fig``, or save."""

    fig: Figure
    ax: Axes
    rc: dict[str, Any] = field(default_factory=dict, repr=False)

    @contextmanager
    def context(self) -> Iterator[None]:
        """Apply the plot's theme settings: fonts resolve at draw time, so draw inside this.

        Use ``with result.context(): result.fig.savefig(...)`` when saving by hand.
        """
        with mpl.rc_context(self.rc):  # type: ignore[arg-type]
            yield

    def overlaps(self) -> list[tuple[str, str]]:
        """Pairs of overlapping text elements (empty when the layout is clean)."""
        with self.context():
            return text_overlaps(self.fig)

    def save(
        self, path: str | Path, formats: tuple[str, ...] = ("png",), dpi: int = 300
    ) -> list[Path]:
        """Write ``path.png`` (or each of ``formats``) cropped and centered with equal padding.

        Add ``formats=("pdf", "svg")`` for vector output and ``dpi`` for the raster resolution.
        """
        with self.context():
            return save_figure(self.fig, path, formats=formats, dpi=dpi)

    def to_array(self) -> np.ndarray:
        """Return rendered RGBA pixels (for tests and image comparison)."""
        with self.context():
            canvas = FigureCanvasAgg(self.fig)
            canvas.draw()  # type: ignore[no-untyped-call]
            return np.asarray(canvas.buffer_rgba()).copy()  # type: ignore[no-untyped-call]


class BasePlot(ABC):
    """Template for all plots; subclasses implement :meth:`draw` (and may override hooks).

    Parameters
    ----------
    x_name, y_name
        Axis labels. Plots that read columns also use them as column names.
    title
        Title (bold, left-aligned).
    data
        pandas or polars table, array-like or mapping (see each plot).
    subtitle
        Optional line(s) under the title: regular weight, muted, one level below it.
    caption
        Optional note centered below the whole figure (wraps to the figure width).
    style
        Registered style name (``"editorial"``, ``"cobalt"``) or a ``Variant``.
    size
        ``"single"`` (3.5 in), ``"double"`` (7.2 in) or ``(width, height)`` inches.
    aspect
        Width / height; defaults to the plot's own.
    x, y
        Column names for x / y when they differ from the axis labels.
    ax
        Draw into an existing axes instead of creating a figure.
    save
        Path (without suffix) to write a PNG. Use ``result.save(path, formats=..., dpi=...)`` for
        other formats or resolution.
    xlim, ylim
        ``(low, high)`` axis limits; ``None`` keeps matplotlib's choice. Use them to show
        bounded scores (0-1, percentages) on a scale where small differences stay small.
    **options
        Plot-specific options; unknown names raise ``TypeError``.
    """

    name: ClassVar[str]
    aspect: ClassVar[float] = 4 / 3
    defaults: ClassVar[dict[str, Any]] = {}

    def __init__(
        self,
        x_name: str | None,
        y_name: str | None,
        title: str | None,
        data: Any,
        *,
        style: str | Variant = "editorial",
        size: str | tuple[float, float] = "single",
        aspect: float | None = None,
        x: str | None = None,
        y: str | None = None,
        ax: Axes | None = None,
        save: str | Path | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        subtitle: str | None = None,
        caption: str | None = None,
        **options: Any,
    ) -> None:
        if isinstance(size, str) and size not in _SIZES:
            raise ValueError(f"size must be one of {sorted(_SIZES)} or (w, h); got {size!r}")
        unknown = set(options) - set(self.defaults)
        if unknown:
            raise TypeError(
                f"{self.name}() got unknown option(s) {sorted(unknown)}; "
                f"valid: {sorted(self.defaults)}"
            )
        self.x_name, self.y_name, self.title, self.data = x_name, y_name, title, data
        self.xcol, self.ycol = x or x_name, y or y_name
        self.v = get_variant(style)
        self.size, self.aspect_override, self.ax, self.save = size, aspect, ax, save
        self.xlim, self.ylim = xlim, ylim
        self.subtitle, self.caption = subtitle, caption
        self.top: Axes | None = None  # top marginal of a joint plot: it carries the title
        self.opt: dict[str, Any] = {**self.defaults, **options}

    def figsize(self, prepared: Any) -> tuple[float, float]:
        """Figure size in inches."""
        if isinstance(self.size, tuple):
            return self.size
        return _SIZES[self.size].figsize(self.aspect_override or self.aspect)

    def prepare_data(self) -> Any:
        """Validate and convert ``self.data`` (all backend handling goes through DataAdapter)."""
        return self.data

    @abstractmethod
    def draw(self, ax: Axes, prepared: Any) -> None:
        """Draw the marks."""

    def style_axes(self, ax: Axes) -> None:
        """Axis labels, hairline spines, title."""
        AxisFormatter(self.x_name, self.y_name, upper=self.v.upper_labels).apply(ax)
        TitleFormatter(
            self.title,
            subtitle=self.subtitle,
            color=self.v.muted,
            props=self.v.theme().proportions,
        ).apply(self.top or ax)
        if self.caption:
            add_caption(ax.figure, self.caption, self.v.theme().proportions, self.v.muted)  # type: ignore[arg-type]

    def style_legend(self, ax: Axes) -> None:
        """Legend placed where it overlaps nothing."""
        LegendStyler().apply(ax)

    def finalize(self, ax: Axes) -> None:  # noqa: B027
        """Last-chance hook (limits, aspect)."""

    def render(self) -> PlotResult:
        """Run the template and return the result."""
        prepared = self.prepare_data()
        rc = self.v.theme().rc_params()
        with mpl.rc_context(rc):  # type: ignore[arg-type]
            if self.ax is None:
                fig = Figure(figsize=self.figsize(prepared))
                ax = fig.subplots()
            else:
                ax = self.ax
                fig = ax.figure  # type: ignore[assignment]
            self.draw(ax, prepared)
            self.style_axes(ax)
            self.finalize(ax)
            if self.xlim is not None:
                ax.set_xlim(self.xlim)
            if self.ylim is not None:
                ax.set_ylim(self.ylim)
            self.style_legend(ax)
        result = PlotResult(fig, ax, rc)
        if self.save is not None:
            result.save(self.save)
        return result
