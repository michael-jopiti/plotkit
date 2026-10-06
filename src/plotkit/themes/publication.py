"""Default publication theme."""

from __future__ import annotations

import shutil
from typing import Any

from cycler import cycler

from plotkit.exceptions import ThemeError
from plotkit.palettes.categorical import OKABE_ITO
from plotkit.themes.base import Theme


class PublicationTheme(Theme):
    """White background, sans-serif text, Computer Modern math, print-tuned sizes.

    Parameters
    ----------
    fontsize
        Base font size in points.
    usetex
        Render text with LaTeX using a sans-serif preamble (``sansmath``).
        Off by default.

    Raises
    ------
    ThemeError
        If ``usetex`` is requested and ``latex`` or ``dvipng`` is not on ``PATH``.
    """

    name = "publication"

    def __init__(self, fontsize: float = 8.0, usetex: bool = False) -> None:
        if usetex:
            missing = [b for b in ("latex", "dvipng") if shutil.which(b) is None]
            if missing:
                raise ThemeError(
                    f"usetex=True needs a TeX install; not found on PATH: {', '.join(missing)}. "
                    "Install TeX Live (or MiKTeX) or use usetex=False (the default)."
                )
        self.fontsize = fontsize
        self.usetex = usetex

    def rc_params(self) -> dict[str, Any]:
        """Return the rcParams for this theme."""
        fs = self.fontsize
        rc: dict[str, Any] = {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "figure.constrained_layout.use": True,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": fs,
            "mathtext.fontset": "cm",
            "axes.labelsize": fs,
            "axes.titlesize": fs + 1,
            "axes.titlelocation": "left",
            "axes.titleweight": "normal",
            "xtick.labelsize": fs - 1,
            "ytick.labelsize": fs - 1,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "axes.grid": False,
            "grid.linewidth": 0.4,
            "grid.alpha": 0.3,
            "grid.color": "0.5",
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "lines.linewidth": 1.2,
            "lines.markersize": 4.0,
            "patch.linewidth": 0.6,
            "axes.prop_cycle": cycler(color=OKABE_ITO),
            "legend.frameon": False,
            "legend.fontsize": fs - 1,
            "legend.handlelength": 1.6,
            "legend.handletextpad": 0.5,
            "legend.borderaxespad": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
        }
        if self.usetex:
            rc["text.usetex"] = True
            rc["text.latex.preamble"] = r"\usepackage{sansmath}\sansmath"
        return rc
