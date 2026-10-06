"""Figure export."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure

_FONTS = {"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "path"}


def save_figure(
    fig: Figure,
    path: str | Path,
    formats: Iterable[str] = ("pdf", "svg", "png"),
    dpi: int = 300,
) -> list[Path]:
    """Save ``fig`` once per format, replacing any suffix of ``path``.

    PDF embeds TrueType fonts (type 42); SVG stores glyphs as paths so it renders
    identically everywhere. Raster formats use ``dpi``.

    Returns
    -------
    list of Path
        Written files.
    """
    base = Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    out = []
    with mpl.rc_context(_FONTS):  # type: ignore[arg-type]
        for fmt in formats:
            target = base.with_suffix(f".{fmt}")
            fig.savefig(target, format=fmt, dpi=dpi, bbox_inches="tight")
            out.append(target)
    return out
