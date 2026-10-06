"""Legend styling."""

from __future__ import annotations

from dataclasses import dataclass

from matplotlib.axes import Axes


@dataclass
class LegendStyler:
    """Frameless legend placed outside the axes so it never covers data.

    Parameters
    ----------
    title
        Legend title.
    outside
        Place right of the axes (default). Otherwise use matplotlib's ``"best"``.
    frame
        Draw a thin frame.
    """

    title: str | None = None
    outside: bool = True
    frame: bool = False

    def apply(self, ax: Axes) -> None:
        """Create the legend on ``ax`` when it has labelled artists."""
        handles, labels = ax.get_legend_handles_labels()
        if not handles:
            return
        loc = (
            {"loc": "upper left", "bbox_to_anchor": (1.02, 1.0)}
            if self.outside
            else {"loc": "best"}
        )
        leg = ax.legend(
            handles,
            labels,
            title=self.title,
            frameon=self.frame,
            markerscale=1.0,
            handlelength=1.6,
            title_fontsize=ax.xaxis.label.get_fontsize(),
            **loc,
        )
        if self.frame:
            leg.get_frame().set_linewidth(0.5)
        leg._legend_box.align = "left"  # type: ignore[attr-defined]
