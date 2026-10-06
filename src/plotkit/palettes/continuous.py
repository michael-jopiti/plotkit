"""Continuous palette."""

from __future__ import annotations

import matplotlib as mpl
import numpy as np
from matplotlib.colors import Colormap

from plotkit.palettes.base import Palette


class ContinuousPalette(Palette):
    """Perceptually uniform, CVD-safe colormap (cividis by default).

    Parameters
    ----------
    source
        Name of a matplotlib colormap, or a :class:`~matplotlib.colors.Colormap`.
    n
        Number of samples stored in ``colors``.
    name
        Palette name; defaults to the colormap's name.
    """

    def __init__(
        self, source: str | Colormap = "cividis", n: int = 256, name: str | None = None
    ) -> None:
        cmap = mpl.colormaps[source] if isinstance(source, str) else source
        object.__setattr__(self, "_source", cmap)
        super().__init__(name or cmap.name, cmap(np.linspace(0, 1, n))[:, :3])

    def _make_cmap(self) -> Colormap:
        return self._source  # type: ignore[attr-defined, no-any-return]
