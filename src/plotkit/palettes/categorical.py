"""Categorical (unordered) palette based on Okabe-Ito."""

from __future__ import annotations

from collections.abc import Sequence

from matplotlib.colors import Colormap, ListedColormap

from plotkit.exceptions import PaletteError
from plotkit.palettes.base import Palette

OKABE_ITO = (
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#000000",  # black
)


class CategoricalPalette(Palette):
    """Up to 8 distinguishable unordered colors (Okabe-Ito by default).

    Parameters
    ----------
    n
        Number of categories, 1 to ``len(colors)``. Defaults to all of them.
    colors
        Source colors, in priority order.
    name
        Palette name prefix.

    Raises
    ------
    PaletteError
        If ``n`` exceeds the available colors: more cannot stay distinguishable.
    """

    def __init__(
        self,
        n: int | None = None,
        colors: Sequence[str] = OKABE_ITO,
        name: str = "okabe-ito",
    ) -> None:
        n = len(colors) if n is None else n
        if not 1 <= n <= len(colors):
            raise PaletteError(
                f"CategoricalPalette supports 1 to {len(colors)} categories, got {n}; "
                "group rare categories or use markers/facets instead"
            )
        super().__init__(f"{name}-{n}", colors[:n])

    def _make_cmap(self) -> Colormap:
        return ListedColormap(list(self.colors), name=self.name)
