"""Volcano plot for differential expression."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from plotkit.data import DataAdapter
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot


@register_plot("volcano")
class VolcanoPlot(BasePlot):
    """log2 fold change against -log10 p, from columns ``lfc`` and ``p`` of a table.

    Options: ``lfc="log2fc"``, ``p="pvalue"``, ``lfc_cut=1.0``, ``p_cut=0.01``. Up and down
    genes get different colors and marker shapes; the rest is muted. Legend shows counts.
    """

    aspect = 1.15
    defaults = {"lfc": "log2fc", "p": "pvalue", "lfc_cut": 1.0, "p_cut": 0.01}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``lfc``, ``nlp`` (-log10 p) and ``state`` (Up / Down / n.s.)."""
        o = self.opt
        d = DataAdapter.normalize(self.data, lfc=o["lfc"], p=o["p"]).frame
        d["nlp"] = -np.log10(np.clip(d["p"].to_numpy(dtype=float), 1e-300, 1.0))
        sig = d["nlp"] > -np.log10(o["p_cut"])
        d["state"] = np.where(
            sig & (d["lfc"] > o["lfc_cut"]),
            "Up",
            np.where(sig & (d["lfc"] < -o["lfc_cut"]), "Down", "n.s."),
        )
        return d

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """Scatter by state, plus dotted thresholds."""
        v, o = self.v, self.opt
        up, down = v.categorical(2).colors
        look = {
            "n.s.": (v.muted, "o", 5, 0.45),
            "Down": (down, "v", 12, 1.0),
            "Up": (up, "^", 12, 1.0),
        }
        for state in ("n.s.", "Down", "Up"):
            color, marker, size, alpha = look[state]
            sub = d[d["state"] == state]
            ax.scatter(
                sub["lfc"],
                sub["nlp"],
                s=size,
                color=color,
                marker=marker,
                alpha=alpha,
                linewidths=0,
                label=f"{state} ({len(sub)})",
            )
        for x in (-o["lfc_cut"], o["lfc_cut"]):
            ax.axvline(x, color=v.muted, lw=v.hairline, ls=":")
        ax.axhline(-np.log10(o["p_cut"]), color=v.muted, lw=v.hairline, ls=":")
