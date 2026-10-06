import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from plotkit.components import SINGLE_COLUMN, LegendStyler, Obstacles, text_overlaps
from plotkit.themes import PublicationTheme
from plotkit.themes.proportions import Proportions


def _fig():
    fig = Figure(figsize=SINGLE_COLUMN.figsize())
    return fig, fig.subplots()


def _legend_box(ax):
    ax.figure.draw_without_rendering()
    return ax.get_legend().get_window_extent()


def _assert_clear(ax, leg_box):
    # outside the axes counts as clear; inside must hit no data
    axes_box = ax.get_window_extent()
    if not axes_box.contains(leg_box.x0, leg_box.y0) or not axes_box.contains(
        leg_box.x1, leg_box.y1
    ):
        return
    assert Obstacles(ax).score(leg_box) == 0


def test_legend_picks_free_corner():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], label="diag")  # diagonal blocks upper-left? no: frees UL and LR
    leg = LegendStyler().apply(ax)
    assert leg is not None
    _assert_clear(ax, _legend_box(ax))


def test_legend_goes_outside_when_crowded():
    fig, ax = _fig()
    x = np.linspace(0, 1, 50)
    for k in range(6):  # dense curves fill the whole axes
        ax.plot(x, k / 5 + 0 * x, label=f"line {k}")
    for k in range(6):
        ax.plot(0 * x + k / 5, x)
    LegendStyler().apply(ax)
    fig.draw_without_rendering()
    assert _legend_box(ax).x0 >= ax.get_window_extent().x1 - 1


def test_line_segments_checked_not_just_vertices():
    """Two-vertex line crossing the legend corner: matplotlib 'best' misses it."""
    fig, ax = _fig()
    ax.plot([0, 1], [1, 0], label="anti")  # passes through the middle only via segment
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.draw_without_rendering()
    obs = Obstacles(ax)
    mid = Bbox.from_extents(
        *(ax.transData.transform((0.45, 0.45)) - 3), *(ax.transData.transform((0.55, 0.55)) + 3)
    )
    assert obs.score(mid) > 0


def test_obstacles_cover_bars_and_images():
    fig, ax = _fig()
    ax.bar([0, 1], [1, 1], label="b")
    fig.draw_without_rendering()
    assert len(Obstacles(ax).boxes) == 2
    fig2, ax2 = _fig()
    ax2.imshow(np.zeros((3, 3)))
    ax2.plot([0], [0], label="p")
    LegendStyler().apply(ax2)  # image covers all: must go outside
    assert _legend_box(ax2).x0 >= ax2.get_window_extent().x1 - 1


@pytest.mark.parametrize("seed", range(5))
def test_random_scatter_never_overlaps(seed):
    rng = np.random.default_rng(seed)
    with PublicationTheme().context():
        fig, ax = _fig()
        for g in "abc":
            ax.scatter(*rng.normal(size=(2, 40)), s=14, label=g)
        LegendStyler(title="g").apply(ax)
        _assert_clear(ax, _legend_box(ax))
        assert text_overlaps(fig) == []


def test_text_overlaps_detects_collision():
    fig, ax = _fig()
    ax.set_xlabel("x" * 5)
    ax.set_title("t")
    assert text_overlaps(fig) == []
    ax.set_xlabel("x" * 5, labelpad=-14)  # drag label onto tick labels
    assert ("ax0.xtick", "ax0.xlabel") in text_overlaps(fig) or (
        "ax0.xlabel",
        "ax0.xtick",
    ) in text_overlaps(fig)


def test_proportions_rules():
    for base in (6.0, 7.0, 8.0, 9.0, 10.0):
        p = Proportions(base)
        assert 5.0 <= p.tick <= p.label <= p.title
        assert p.data_lw >= 2 * p.axis_lw
        assert p.axis_lw >= 0.25 and p.grid_lw >= 0.25
        assert p.tick_length < p.label / 2


def test_theme_uses_proportions_and_helvetica():
    rc = PublicationTheme(fontsize=8).rc_params()
    assert rc["font.sans-serif"][0] == "Helvetica"
    p = Proportions(8)
    assert rc["axes.titlesize"] == p.title and rc["xtick.labelsize"] == p.tick
    assert rc["lines.linewidth"] == p.data_lw and rc["axes.linewidth"] == p.axis_lw


def test_colorbar_slim_and_clear():
    from plotkit.components import add_colorbar

    fig, ax = _fig()
    sc = ax.scatter([0, 1], [0, 1], c=[0, 1])
    cbar = add_colorbar(ax, sc, "z (a.u.)")
    fig.draw_without_rendering()
    assert cbar.ax.get_window_extent().width < 0.1 * ax.get_window_extent().width
    assert text_overlaps(fig) == []
