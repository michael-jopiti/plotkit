"""Categorical (unordered) palette based on Okabe-Ito."""

from __future__ import annotations

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
    """Up to 8 distinguishable unordered colors (Okabe-Ito).

    Parameters
    ----------
    n
        Number of categories, 1 to 8.

    Raises
    ------
    PaletteError
        If ``n`` exceeds 8: more colors cannot stay distinguishable.
    """

    def __init__(self, n: int = 8) -> None:
        if not 1 <= n <= len(OKABE_ITO):
            raise PaletteError(
                f"CategoricalPalette supports 1 to {len(OKABE_ITO)} categories, got {n}; "
                "group rare categories or use markers/facets instead"
            )
        super().__init__(f"okabe-ito-{n}", OKABE_ITO[:n])

    def _make_cmap(self) -> Colormap:
        return ListedColormap(list(self.colors), name=self.name)
