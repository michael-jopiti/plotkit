"""Repo-wide invariants: API/registry agreement, every plot x style, grids, styles, docs."""

import ast
import inspect
import re
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image
import numpy as np
import pytest
from matplotlib.colors import to_rgb

import plotkit
from plotkit import Panel
from plotkit.plots import plots
from plotkit.themes.styled import variants
from tests.test_api import CASES

ROOT = Path(__file__).resolve().parents[1]
STYLES = ["editorial", "cobalt"]
CASE_NAMES = list(CASES)


def _lum(c: str) -> float:
    r, g, b = (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in to_rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_public_names_exist():
    assert all(hasattr(plotkit, n) for n in plotkit.__all__)
    assert plotkit.__version__ == version("plotkit")


@pytest.mark.parametrize("kind", plots.names())
def test_every_plot_has_a_matching_wrapper(kind):
    fn = getattr(plotkit, kind)
    params = inspect.signature(fn).parameters
    defaults = plots.get(kind).defaults
    assert set(defaults) <= set(params), f"{kind}: options missing from the wrapper"
    for name, value in defaults.items():
        assert params[name].default == value, f"{kind}.{name}: wrapper default differs"


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("name", CASE_NAMES)
def test_plot_clean_and_deterministic_in_every_style(name, style):
    kind, args, opts = CASES[name]()
    draw = lambda: plotkit.plot(kind, *args, **opts, style=style)  # noqa: E731
    assert draw().overlaps() == []
    # overlaps() before to_array() re-runs layout and can shift colorbars: compare fresh draws
    assert np.array_equal(draw().to_array(), draw().to_array())


@pytest.mark.parametrize("name", CASE_NAMES)
def test_saved_png_has_equal_margins(name, tmp_path):
    kind, args, opts = CASES[name]()
    plotkit.plot(kind, *args, **opts, save=tmp_path / "f")
    img = matplotlib.image.imread(tmp_path / "f.png")[..., :3]
    ink = (np.abs(img - img[0, 0]) > 2 / 255).any(-1)
    rows, cols = np.flatnonzero(ink.any(1)), np.flatnonzero(ink.any(0))
    h, w = ink.shape
    margins = {cols[0], w - 1 - cols[-1], rows[0], h - 1 - rows[-1]}
    assert max(margins) - min(margins) <= 1


@pytest.mark.parametrize("name", CASE_NAMES)
def test_numpy_and_list_inputs_match_pandas(name):
    kind, args, opts = CASES[name]()
    data = args[3]
    if hasattr(data, "to_dict"):  # tables are covered by the polars parity test
        return
    ref = plotkit.plot(kind, *args, **opts).to_array()
    for alt in (np.asarray(data), list(data)):
        assert np.array_equal(ref, plotkit.plot(kind, *args[:3], alt, **opts).to_array())


@pytest.mark.parametrize("style", STYLES)
def test_grid_of_every_plot_has_no_overlaps(style):
    cells = [
        Panel(k, *a, **o, subtitle="sub", caption="A caption long enough to wrap " * 2)
        for k, a, o in (CASES[n]() for n in CASE_NAMES)
    ]
    rows = [cells[i : i + 2] for i in range(0, len(cells), 2)]  # 3 columns crowd heatmap ticks
    res = plotkit.grid(rows, "Title", "Subtitle", "Figure caption", style=style)
    assert res.axes.shape == (len(rows), 2) and res.overlaps() == []


@pytest.mark.parametrize("shape", [(1, 1), (1, 3), (3, 1)])
def test_grid_shapes(shape):
    k, a, o = CASES["boxplot"]()
    res = plotkit.grid([[Panel(k, *a, **o) for _ in range(shape[1])] for _ in range(shape[0])])
    assert res.axes.shape == shape and res.overlaps() == []


@pytest.mark.parametrize("style", sorted(variants.names()))
def test_style_contrast_and_registration(style):
    v = variants.get(style)
    assert contrast(v.fg, v.bg) >= 4.5 and contrast(v.muted, v.bg) >= 4.5
    assert all(contrast(c, v.bg) >= 2.9 for c in v.categorical().to_hex())  # 3:1, hex rounding
    for suffix in ("categorical", "discrete", "continuous"):
        assert plotkit.palettes.get_palette(f"{style}-{suffix}", None) is not None


def test_readme_documents_every_plot_and_snippets_parse():
    text = (ROOT / "README.md").read_text()
    for kind in (k for k in plots.names() if hasattr(plotkit, k)):  # skip test-registered plots
        assert f"`{kind}`" in text, f"README plot reference lacks {kind}"
    for block in re.findall(r"```python\n(.*?)```", text, re.S):
        ast.parse(block)
    for src in re.findall(r'src="(examples/[^"]+)"', text):
        assert (ROOT / src).exists(), f"README image missing: {src}"
