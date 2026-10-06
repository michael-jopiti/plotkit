"""Default publication theme."""

from __future__ import annotations

import shutil
from typing import Any

from cycler import cycler

from plotkit.exceptions import ThemeError
from plotkit.palettes.categorical import OKABE_ITO
from plotkit.themes.base import Theme
from plotkit.themes.proportions import Proportions

_FONTS = ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans", "DejaVu Sans"]


class PublicationTheme(Theme):
    """White background, sans-serif text, Computer Modern math, print-tuned sizes.

    Sizes follow :class:`~plotkit.themes.proportions.Proportions`. The font is
    Helvetica, falling back to its metric-compatible clone Nimbus Sans, then Arial.

    Parameters
    ----------
    fontsize
        Axis-label font size in points; everything else is derived from it.
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
        self.proportions = Proportions(fontsize)

    def rc_params(self) -> dict[str, Any]:
        """Return the rcParams for this theme."""
        p = self.proportions
        rc: dict[str, Any] = {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "figure.constrained_layout.use": True,
            "figure.constrained_layout.h_pad": p.layout_pad,
            "figure.constrained_layout.w_pad": p.layout_pad,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": p.layout_pad,
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Helvetica",
                "Nimbus Sans",
                "Arial",
                "Liberation Sans",
                "DejaVu Sans",
            ],
            "font.size": p.label,
            "mathtext.fontset": "cm",
            "axes.labelsize": p.label,
            "axes.labelpad": p.label_pad,
            "axes.titlesize": p.title,
            "axes.titlepad": p.title_pad,
            "axes.titlelocation": "left",
            "axes.titleweight": "normal",
            "xtick.labelsize": p.tick,
            "ytick.labelsize": p.tick,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": p.axis_lw,
            "axes.grid": False,
            "grid.linewidth": p.grid_lw,
            "grid.alpha": 0.5,
            "grid.color": "0.7",
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": p.axis_lw,
            "ytick.major.width": p.axis_lw,
            "xtick.major.size": p.tick_length,
            "ytick.major.size": p.tick_length,
            "xtick.major.pad": p.tick_pad,
            "ytick.major.pad": p.tick_pad,
            "lines.linewidth": p.data_lw,
            "lines.markersize": p.marker,
            "lines.markeredgewidth": p.axis_lw,
            "patch.linewidth": p.axis_lw,
            "axes.prop_cycle": cycler(color=OKABE_ITO),
            "legend.frameon": False,
            "legend.fontsize": p.tick,
            "legend.title_fontsize": p.label,
            "legend.handlelength": 2.0,
            "legend.handletextpad": 0.6,
            "legend.labelspacing": 0.4,
            "legend.columnspacing": 1.5,
            "legend.borderpad": 0.3,
            "legend.borderaxespad": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
        }
        if self.usetex:
            rc["text.usetex"] = True
            rc["text.latex.preamble"] = r"\usepackage{sansmath}\sansmath"
        return rc
