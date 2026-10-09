"""Figure export."""

from __future__ import annotations

import io
from collections.abc import Iterable
from pathlib import Path

import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

_SUFFIXES = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".eps", ".ps", ".webp"}
_FONTS = {"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "path"}


def _ink_bbox(fig: Figure, pad_inches: float, probe_dpi: int = 300) -> Bbox:
    """Bounding box (inches) of everything drawn, grown by ``pad_inches`` on every side.

    The probe canvas extends 1 inch past the figure so overflowing text is not clipped.
    """
    w_in, h_in = fig.get_size_inches()
    m = 1.0
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=probe_dpi, bbox_inches=Bbox.from_extents(-m, -m, w_in + m, h_in + m)
    )
    buf.seek(0)
    img = mpl.image.imread(buf)[..., :3]
    ink = (np.abs(img - img[0, 0]) > 2 / 255).any(-1)
    rows, cols = np.flatnonzero(ink.any(1)), np.flatnonzero(ink.any(0))
    if not len(rows):
        return Bbox.from_bounds(0, 0, w_in, h_in)
    h = img.shape[0]
    x0, x1 = cols[0] / probe_dpi - m, (cols[-1] + 1) / probe_dpi - m
    y0, y1 = (h - rows[-1] - 1) / probe_dpi - m, (h - rows[0]) / probe_dpi - m
    return Bbox.from_extents(x0 - pad_inches, y0 - pad_inches, x1 + pad_inches, y1 + pad_inches)


def save_figure(
    fig: Figure,
    path: str | Path,
    formats: Iterable[str] = ("png",),
    dpi: int = 300,
    pad_inches: float = 0.15,
) -> list[Path]:
    """Save ``fig`` once per format, replacing a trailing image suffix of ``path``.

    PNG only by default; pass ``formats=("pdf", "svg")`` and ``dpi`` for others.
    ``"out/fig.png"`` and ``"out/fig"`` both write ``out/fig.<fmt>``; any other dot
    (``"out/fig_0.5"``) is part of the name and is kept.

    The output is cropped to the drawn ink and padded by ``pad_inches`` on all four
    sides, so the figure sits exactly centered in the image. PDF embeds TrueType
    fonts (type 42); SVG stores glyphs as paths so it renders identically
    everywhere. Raster formats use ``dpi``.

    Returns
    -------
    list of Path
        Written files.
    """
    base = Path(path)
    if base.suffix.lower() in _SUFFIXES:
        base = base.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)
    out = []
    with mpl.rc_context(_FONTS):  # type: ignore[arg-type]
        box = _ink_bbox(fig, pad_inches)
        for fmt in formats:
            target = base.with_name(f"{base.name}.{fmt}")
            fig.savefig(target, format=fmt, dpi=dpi, bbox_inches=box)
            out.append(target)
    return out
