import matplotlib
import pytest

matplotlib.use("Agg")

import plotkit
from plotkit import Panel
from plotkit import synthetic as syn


def panels():
    return [
        [
            Panel(
                "continuous",
                "Value",
                "Density",
                "A",
                syn.gaussian(2, 0.5),
                subtitle="s",
                caption="c " * 40,
            ),
            Panel("boxplot", "Group", "Value", "B", syn.groups(), caption="Boxes."),
        ],
        [Panel("bar", "Region", "Usage (%)", "C", syn.region_usage(), hue="condition"), None],
    ]


def test_grid_no_overlaps_and_texts():
    r = plotkit.grid(panels(), "Fig title", "Fig subtitle", "Fig caption")
    assert r.axes.shape == (2, 2) and r.ax is r.axes[0, 0]
    assert r.overlaps() == []
    assert {t.get_text() for t in r.fig.texts} >= {"Fig title", "Fig subtitle"}
    assert len(r.axes[0, 0].texts) == 2  # panel subtitle + panel caption


def test_grid_saves(tmp_path):
    assert plotkit.grid(panels(), save=tmp_path / "g")  # no figure-level text
    assert (tmp_path / "g.png").exists()


def test_grid_rejects_bad_input():
    with pytest.raises(ValueError, match="same length"):
        plotkit.grid([[panels()[0][0]], panels()[0]])
    with pytest.raises(ValueError, match="non-empty"):
        plotkit.grid([])
    with pytest.raises(TypeError, match="figure-wide"):
        Panel("boxplot", "G", "V", "T", syn.groups(), style="cobalt")
