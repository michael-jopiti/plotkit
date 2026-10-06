"""Abstract palette."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from matplotlib.colors import Colormap, to_hex, to_rgb
from matplotlib.figure import Figure

RGB = tuple[float, float, float]


class Palette(ABC):
    """Immutable color palette.

    Subclasses implement :meth:`_make_cmap`. Attributes cannot be reassigned.

    Parameters
    ----------
    name
        Palette name.
    colors
        Sequence of colors (anything matplotlib accepts).
    """

    name: str
    colors: tuple[RGB, ...]

    def __init__(self, name: str, colors: Any) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "colors", tuple(to_rgb(c) for c in colors))
        object.__setattr__(self, "_cmap", self._make_cmap())

    def __setattr__(self, key: str, value: Any) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __delattr__(self, key: str) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    @abstractmethod
    def _make_cmap(self) -> Colormap:
        """Build the matplotlib colormap for ``self.colors``."""

    @property
    def cmap(self) -> Colormap:
        """A copy of the matplotlib colormap (safe to mutate)."""
        return self._cmap.copy()  # type: ignore[attr-defined, no-any-return]

    @property
    def n(self) -> int:
        """Number of colors."""
        return len(self.colors)

    def to_hex(self) -> list[str]:
        """Colors as ``#rrggbb`` strings."""
        return [to_hex(c) for c in self.colors]

    def show(self) -> Figure:
        """Swatch preview. Returns a pyplot-free :class:`~matplotlib.figure.Figure`."""
        fig = Figure(figsize=(max(2.0, 0.5 * self.n), 0.9))
        ax = fig.subplots()
        ax.imshow([list(self.colors)], aspect="auto", interpolation="nearest")
        ax.set_axis_off()
        ax.set_title(f"{self.name} (n={self.n})", fontsize=8, loc="left")
        return fig

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, n={self.n})"
