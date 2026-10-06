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
        Matplotlib colormap name or :class:`~matplotlib.colors.Colormap` to sample.
    span
        Part of the ramp to sample, as ``(start, stop)`` fractions in ``[0, 1]``.
        Trimming the light end keeps thin lines visible on a light background.
    """

    def __init__(
        self,
        n: int = 5,
        source: str | Colormap = "viridis",
        span: tuple[float, float] = (0.0, 0.95),
    ) -> None:
        if not 3 <= n <= 9:
            raise PaletteError(f"DiscretePalette supports 3 to 9 steps, got {n}")
        cmap = mpl.colormaps[source] if isinstance(source, str) else source
        super().__init__(f"{cmap.name}-{n}", cmap(np.linspace(*span, n))[:, :3])

    def _make_cmap(self) -> Colormap:
        return ListedColormap(list(self.colors), name=self.name)
