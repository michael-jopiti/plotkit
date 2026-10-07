"""Kaplan-Meier survival curves."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot

STYLES = ("-", "--", "-.", ":", (0, (5, 1)))


def kaplan_meier(time: np.ndarray, event: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Kaplan-Meier estimate: event times and survival probability just after each."""
    g = pd.DataFrame({"t": time, "e": event.astype(int)}).groupby("t")["e"].agg(["sum", "count"])
    at_risk = len(time) - np.r_[0, g["count"].cumsum().to_numpy()[:-1]]
    return g.index.to_numpy(dtype=float), np.cumprod(1 - g["sum"].to_numpy() / at_risk)


@register_plot("survival")
class SurvivalPlot(BasePlot):
    """Survival curves from a table with time, event (1 = event, 0 = censored) and group columns.

    Options: ``time="time"``, ``event="event"``, ``group="group"`` (a missing group column
    gives a single curve). Censored observations are marked with ticks; groups differ by
    line style as well as color.
    """

    defaults = {"time": "time", "event": "event", "group": "group"}

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``t``, ``e`` and ``g``."""
        o = self.opt
        frame = DataAdapter.to_frame(self.data)
        group = o["group"] if o["group"] in frame.columns else None
        if group is None and o["group"] != self.defaults["group"]:
            raise DataError(f"group column {o['group']!r} not found in {list(frame.columns)}")
        d = DataAdapter.normalize(frame, t=o["time"], e=o["event"], g=group).frame
        if "g" not in d:
            d["g"] = ""
        return d

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """One step curve per group."""
        v = self.v
        groups = list(dict.fromkeys(d["g"]))
        pal = v.categorical(len(groups))
        for i, (grp, color) in enumerate(zip(groups, pal.colors, strict=True)):
            sub = d[d["g"] == grp]
            t, s = kaplan_meier(sub["t"].to_numpy(dtype=float), sub["e"].to_numpy())
            ls = STYLES[i % len(STYLES)]
            ax.step(
                np.r_[0, t],
                np.r_[1, s],
                where="post",
                color=color,
                ls=ls,
                label=str(grp) if grp != "" else None,
            )
            cens = sub.loc[sub["e"] == 0, "t"].to_numpy(dtype=float)
            at = np.searchsorted(t, cens, side="right") - 1
            ax.plot(
                cens,
                np.where(at >= 0, s[np.maximum(at, 0)], 1.0),
                "|",
                color=color,
                ms=4,
                mew=v.hairline * 1.5,
            )

    def finalize(self, ax: Axes) -> None:
        """Probability axis from 0 to 1."""
        ax.set_ylim(0, 1.05)
        ax.set_xlim(left=0)
