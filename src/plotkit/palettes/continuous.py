"""Continuous palette."""

from __future__ import annotations

import matplotlib as mpl
import numpy as np
from matplotlib.colors import Colormap

from plotkit.palettes.base import Palette


class ContinuousPalette(Palette):
    """Perceptually uniform, CVD-safe colormap (viridis family by default).

    Parameters
    ----------
    source
        Name of a matplotlib colormap, e.g. ``"cividis"`` or ``"viridis"``.
    n
        Number of samples stored in ``colors``.
    """

    def __init__(self, source: str = "cividis", n: int = 256) -> None:
        super().__init__(source, mpl.colormaps[source](np.linspace(0, 1, n))[:, :3])

    def _make_cmap(self) -> Colormap:
        return mpl.colormaps[self.name]
