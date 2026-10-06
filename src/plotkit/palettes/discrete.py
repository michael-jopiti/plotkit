"""Discrete ordered palette."""

from __future__ import annotations

import matplotlib as mpl
import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from plotkit.exceptions import PaletteError
from plotkit.palettes.base import Palette


class DiscretePalette(Palette):
    """``n`` ordered steps (3 to 9) sampled from a perceptually uniform ramp.

    Lightness increases monotonically with index, so order survives grayscale.

    Parameters
    ----------
    n
        Number of steps, 3 to 9.
    source
        Matplotlib colormap to sample.
    """

    def __init__(self, n: int = 5, source: str = "viridis") -> None:
        if not 3 <= n <= 9:
            raise PaletteError(f"DiscretePalette supports 3 to 9 steps, got {n}")
        colors = mpl.colormaps[source](np.linspace(0.0, 0.95, n))[:, :3]
        super().__init__(f"{source}-{n}", colors)

    def _make_cmap(self) -> Colormap:
        return ListedColormap(list(self.colors), name=self.name)
