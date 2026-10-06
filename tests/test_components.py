import matplotlib

matplotlib.use("Agg")
import pytest
from matplotlib.figure import Figure

from plotkit.components import (
    DOUBLE_COLUMN,
    SINGLE_COLUMN,
    AxisFormatter,
    LegendStyler,
    TitleFormatter,
    with_unit,
)
from plotkit.io import save_figure


def test_size():
    assert SINGLE_COLUMN.figsize(aspect=2) == (3.5, 1.75)
    assert DOUBLE_COLUMN.figsize(height=3) == (7.2, 3)


def test_axis_title_legend():
    ax = Figure().subplots()
    ax.plot([0, 1], label="a")
    AxisFormatter("Time", "Signal", "s", "mV", grid=True).apply(ax)
    TitleFormatter("T").apply(ax)
    LegendStyler(title="g", frame=True).apply(ax)
    assert ax.get_xlabel() == "Time (s)" == with_unit("Time", "s")
    assert not ax.spines["top"].get_visible() and not ax.spines["right"].get_visible()
    assert ax.get_title(loc="left") == "T"
    leg = ax.get_legend()
    assert leg.get_frame_on() and leg.get_title().get_text() == "g"
    ax2 = Figure().subplots()
    assert LegendStyler().apply(ax2) is None
    ax2.plot([0], label="b")
    LegendStyler(auto=False, loc="upper left").apply(ax2)
    assert not ax2.get_legend().get_frame_on()


@pytest.mark.parametrize("dpi", [300])
def test_save_figure(tmp_path, dpi):
    fig = Figure()
    fig.subplots().plot([0, 1])
    files = save_figure(fig, tmp_path / "sub" / "f.png", dpi=dpi)
    assert [f.suffix for f in files] == [".pdf", ".svg", ".png"]
    assert all(f.stat().st_size > 0 for f in files)
    assert b"/FontFile2" in files[0].read_bytes()
