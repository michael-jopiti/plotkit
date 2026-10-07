"""Typographic scale and stroke proportions derived from one base size."""

from __future__ import annotations

from dataclasses import dataclass


def _snap(points: float) -> float:
    """Round to the nearest half point, as fonts are specified in print."""
    return round(points * 2) / 2


@dataclass(frozen=True)
class Proportions:
    """Every size in a figure follows from ``base`` (the axis-label size, in points).

    Rules applied:

    * Modular type scale with a major-second ratio (1.125): tick and legend text
      is one step below labels, titles one step above. Text never drops below 5 pt
      (the minimum accepted by Nature and Science).
    * Data strokes are about twice as heavy as the axis furniture, so data leads
      and axes recede. Nothing is thinner than the 0.25 pt print hairline.
    * Tick length is about 0.4 em, markers about 0.5 em, grid lines half a spine.
    * Gaps (label pad, title pad, legend spacing) are fractions of an em, so
      white space scales with the type.

    Parameters
    ----------
    base
        Axis-label font size in points.
    ratio
        Modular-scale ratio between adjacent type levels.
    """

    base: float = 8.0
    ratio: float = 1.125

    @property
    def label(self) -> float:
        """Axis-label size (pt)."""
        return self.base

    @property
    def tick(self) -> float:
        """Tick-label and legend text size (pt), one step below labels."""
        return max(5.0, _snap(self.base / self.ratio))

    @property
    def title(self) -> float:
        """Title size (pt), one step above labels."""
        return _snap(self.base * self.ratio)

    @property
    def axis_lw(self) -> float:
        """Spine and tick stroke width (pt)."""
        return max(0.25, round(self.base * 0.075, 2))

    @property
    def data_lw(self) -> float:
        """Data line width (pt), about twice the axis stroke."""
        return round(2 * self.axis_lw + 0.05, 2)

    @property
    def grid_lw(self) -> float:
        """Grid line width (pt)."""
        return max(0.25, round(self.axis_lw / 2, 2))

    @property
    def tick_length(self) -> float:
        """Major tick length (pt)."""
        return round(self.base * 0.4, 1)

    @property
    def tick_pad(self) -> float:
        """Gap between tick and tick label (pt)."""
        return round(self.base * 0.35, 1)

    @property
    def label_pad(self) -> float:
        """Gap between tick labels and axis label (pt)."""
        return round(self.base * 0.5, 1)

    @property
    def title_pad(self) -> float:
        """Gap between axes and title (pt)."""
        return round(self.base * 0.9, 1)

    @property
    def subtitle(self) -> float:
        """Subtitle size (pt): the label size, regular weight, so the bold title leads."""
        return self.label

    @property
    def subtitle_gap(self) -> float:
        """Gap between title baseline block and subtitle block (pt)."""
        return round(self.base * 0.35, 1)

    @property
    def caption(self) -> float:
        """Caption size (pt), one step below labels."""
        return self.tick

    @property
    def marker(self) -> float:
        """Marker size (pt)."""
        return round(self.base * 0.5, 1)

    @property
    def layout_pad(self) -> float:
        """Outer figure padding for constrained layout (inches)."""
        return round(self.base * 0.5 / 72, 3)
