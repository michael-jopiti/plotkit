"""CVD validation helpers (dev-only: need colorspacious). Shared by tests and examples."""

import itertools

import numpy as np
from colorspacious import cspace_convert

CVD = [None] + [
    {"name": "sRGB1+CVD", "cvd_type": t, "severity": 100}
    for t in ("deuteranomaly", "protanomaly", "tritanomaly")
]


def _rgb(hexes):
    return np.array([[int(h[i : i + 2], 16) / 255 for i in (1, 3, 5)] for h in hexes])


def to_ucs(hexes, cvd=None):
    rgb = _rgb(hexes)
    if cvd:
        rgb = np.clip(cspace_convert(rgb, cvd, "sRGB1"), 0, 1)
    return cspace_convert(rgb, "sRGB1", "CAM02-UCS")


def min_delta_e(hexes):
    """Smallest pairwise distance across normal vision and three CVD simulations."""
    return min(
        min(np.linalg.norm(a - b) for a, b in itertools.combinations(to_ucs(hexes, c), 2))
        for c in CVD
    )


def lightness_monotonic(hexes):
    d = np.diff(to_ucs(hexes)[:, 0])
    return bool(np.all(d > 0) or np.all(d < 0))


def contrast_vs_white(h):
    c = _rgb([h])[0]
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    return 1.05 / (lum + 0.05)
