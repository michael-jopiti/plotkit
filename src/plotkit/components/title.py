"""Title, subtitle and caption: stacked from the axes outward with computed gaps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

from plotkit.themes.proportions import Proportions


@dataclass
class TitleFormatter:
    """Left-aligned (default) or centered title with an optional subtitle beneath it.

    Stack, from the axes up: subtitle (regular weight, muted, one size below the title),
    a fixed gap, then the bold title. The subtitle height is computed from its font size
    and line count, so the title is lifted by exactly that much and the two never touch.
    """

    title: str | None = None
    loc: Literal["left", "center"] = "left"
    subtitle: str | None = None
    color: str | None = None
    props: Proportions | None = None

    def apply(self, ax: Axes) -> None:
        """Set the title (and subtitle) on ``ax`` if given."""
        pad = mpl.rcParams["axes.titlepad"]
        if self.subtitle:
            p = self.props or Proportions()
            size = p.subtitle
            note = ax.annotate(
                self.subtitle,
                (0 if self.loc == "left" else 0.5, 1),
                xycoords="axes fraction",
                xytext=(0, pad),
                textcoords="offset points",
                ha=self.loc,
                va="bottom",
                fontsize=size,
                fontweight="normal",
                color=self.color,
                annotation_clip=False,
                gid="subtitle",
            )
            pad += _height_pt(note) + p.subtitle_gap
        if self.title:
            t = ax.set_title(self.title, loc=self.loc, pad=pad)
            if self.subtitle:  # title box reaches below its baseline by the descent
                ax.set_title(self.title, loc=self.loc, pad=pad + _descent_pt(t))


def _renderer(fig: Figure) -> Any:
    return fig._get_renderer()  # type: ignore[attr-defined]


def _height_pt(text: Text) -> float:
    """Return the measured height of ``text`` in points (exact font metrics)."""
    fig = text.get_figure()
    box = text.get_window_extent(_renderer(fig))  # type: ignore[arg-type]
    return float(box.height * 72 / fig.dpi)  # type: ignore[union-attr]


def _descent_pt(text: Text) -> float:
    """Return how far the text box reaches below its baseline, in points."""
    fig = text.get_figure()
    _, _, d = _renderer(fig).get_text_width_height_descent(  # type: ignore[arg-type]
        "lp",
        text.get_fontproperties(),
        False,  # matplotlib boxes text by the descent of "lp"
    )
    return float(d * 72 / fig.dpi)  # type: ignore[union-attr]


def _wrap(fig: Figure, text: str, size: float, width_pt: float) -> str:
    """Greedy word wrap of ``text`` so no line is wider than ``width_pt`` points."""
    r = _renderer(fig)
    props = FontProperties(size=size)

    def fits(line: str) -> bool:
        w, _, _ = r.get_text_width_height_descent(line, props, False)
        return bool(w * 72 / fig.dpi <= width_pt)

    out: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if line and not fits(trial):
                out.append(line)
                trial = word
            line = trial
        out.append(line)
    return "\n".join(out)


def add_caption(fig: Figure, text: str, props: Proportions, color: str | None = None) -> None:
    """Centered caption below the whole figure; constrained layout reserves its space.

    A blank first line holds the gap to the content above (one caption line, about 1.2 em),
    so the layout padding between panels stays untouched.
    """
    width = fig.get_figwidth() * 72 - 2 * props.layout_pad * 72
    fig.supxlabel(
        "\n" + _wrap(fig, text, props.caption, width),
        fontsize=props.caption,
        fontweight="normal",
        color=color,
    )
