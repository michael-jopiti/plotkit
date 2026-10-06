"""Gradient builder and color math used to design and validate the built-in styles."""

import itertools
import sys
from functools import cache
from pathlib import Path

import numpy as np
from colorspacious import cspace_convert
from matplotlib.colors import ListedColormap, to_rgb

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))


CVD = [None] + [
    {"name": "sRGB1+CVD", "cvd_type": t, "severity": 100}
    for t in ("deuteranomaly", "protanomaly", "tritanomaly")
]
MIN_DISCRETE_DE = 6.0


def ucs(rgb, cvd=None):
    """sRGB (0-1) to CAM02-UCS, optionally through a CVD simulation."""
    rgb = np.asarray(rgb, dtype=float)
    if cvd:
        rgb = np.clip(cspace_convert(rgb, cvd, "sRGB1"), 0, 1)
    return cspace_convert(rgb, "sRGB1", "CAM02-UCS")


def min_de(rgb, conditions=CVD):
    """Smallest pairwise CAM02-UCS distance across vision conditions."""
    return min(
        min(np.linalg.norm(a - b) for a, b in itertools.combinations(ucs(rgb, c), 2))
        for c in conditions
    )


def monotonic(values):
    """True when strictly increasing or strictly decreasing."""
    d = np.diff(values)
    return bool((d > 0).all() or (d < 0).all())


def luminance(rgb):
    """Relative luminance (grayscale value) of sRGB colors."""
    c = np.asarray(rgb, dtype=float)
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c @ [0.2126, 0.7152, 0.0722]


def _build(jab, scale, n):
    t = np.linspace(0, 1, n)
    knots = np.linspace(0, 1, len(jab))
    a = np.interp(t, knots, jab[:, 1]) * scale
    b = np.interp(t, knots, jab[:, 2]) * scale
    j = np.linspace(jab[0, 0], jab[-1, 0], n)
    # chroma shrinks per sample until it fits sRGB (clipping would break monotonicity)
    shrink = np.linspace(1, 0, 60)
    cand = np.stack([np.repeat(j[:, None], 60, 1), a[:, None] * shrink, b[:, None] * shrink], -1)
    rgb = cspace_convert(cand.reshape(-1, 3), "CAM02-UCS", "sRGB1").reshape(n, 60, 3)
    fits = ((rgb >= -1e-4) & (rgb <= 1 + 1e-4)).all(-1)
    return np.clip(rgb[np.arange(n), fits.argmax(1)], 0, 1)


def _ramp_ok(rgb, span):
    if not all(monotonic(ucs(rgb, c)[:, 0]) for c in CVD) or not monotonic(luminance(rgb)):
        return False
    steps = np.linspace(*span, 9)
    nine = rgb[np.round(steps * (len(rgb) - 1)).astype(int)]
    return min_de(nine) >= MIN_DISCRETE_DE


@cache
def make_gradient(
    stops: tuple[str, ...], name: str, span: tuple[float, float] = (0.0, 0.9), n: int = 256
) -> tuple[ListedColormap, float]:
    """Smooth gradient through ``stops`` with strictly rising CAM02-UCS lightness.

    Hue and chroma follow the stops; lightness is a linear ramp between the first and
    last stop. Chroma is scaled down (from 100%) until lightness stays monotonic
    under deuteranopia, protanopia, tritanopia and grayscale, and a 9-step sample
    keeps dE >= 6 in every condition.

    Returns
    -------
    (ListedColormap, float)
        The colormap and the chroma scale that was needed (1.0 = untouched stops).
    """
    jab = cspace_convert(np.array([to_rgb(s) for s in stops]), "sRGB1", "CAM02-UCS")
    for scale in np.linspace(1.0, 0.2, 33):
        rgb = _build(jab, scale, n)
        if _ramp_ok(rgb, span):
            return ListedColormap(rgb, name=name), float(scale)
    raise ValueError(f"no CVD-safe chroma scale found for gradient {name!r}")
