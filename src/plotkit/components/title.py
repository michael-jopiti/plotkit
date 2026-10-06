"""Title styling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from matplotlib.axes import Axes


@dataclass
class TitleFormatter:
    """Left-aligned (default) or centered title."""

    title: str | None = None
    loc: Literal["left", "center"] = "left"

    def apply(self, ax: Axes) -> None:
        """Set the title on ``ax`` if one was given."""
        if self.title:
            ax.set_title(self.title, loc=self.loc)
