import matplotlib

matplotlib.use("Agg")
import numpy as np
import pytest

import plotkit
from plotkit import synthetic as syn
from plotkit.data import DataAdapter

pl = pytest.importorskip("polars")

CASES = {
    "continuous": lambda: (
        "continuous",
        ("Value (a.u.)", "Density", "T", syn.gaussian(2, 0.5, 800)),
        {},
    ),
    "boxplot": lambda: ("boxplot", ("Group", "Value (a.u.)", "T", syn.groups(20)), {}),
    "bar": lambda: ("bar", ("Region", "Usage (%)", "T", syn.region_usage()), {"hue": "condition"}),
    "scatter": lambda: ("scatter", ("gene_0", "gene_1", "T", syn.expression(20)), {"hue": "group"}),
    "scatter_color": lambda: (
        "scatter",
        ("gene_0", "gene_1", "T", syn.expression(20)),
        {"color": "gene_2"},
    ),
    "line": lambda: (
        "line",
        ("Time (h)", "Response", "T", syn.dose_response()),
        {"hue": "dose", "ordered": True},
    ),
    "dim_red": lambda: (
        "dim_red",
        ("PC1", "PC2", "T", syn.expression(30)),
        {"hue": "group", "method": "pca"},
    ),
    "survival": lambda: ("survival", ("Time (months)", "Survival", "T", syn.survival_data(40)), {}),
    "volcano": lambda: (
        "volcano",
        ("log2 fold change", "-log10 p", "T", syn.differential_expression(600)),
        {},
    ),
    "heatmap": lambda: ("heatmap", ("Samples", "Genes", "T", syn.expression_matrix(6)), {}),
}


def to_polars(x):
    if hasattr(x, "to_dict"):
        return pl.DataFrame(x.to_dict(orient="list"))
    return pl.Series(x)


@pytest.mark.parametrize("name", CASES)
def test_plot_runs_clean_and_saves(name, tmp_path):
    kind, args, opts = CASES[name]()
    res = plotkit.plot(kind, *args, **opts, save=tmp_path / name)
    assert res.overlaps() == []
    assert {p.suffix for p in tmp_path.iterdir()} == {".pdf", ".svg", ".png"}
    assert getattr(plotkit, kind)(*args, **opts).ax is not None


@pytest.mark.parametrize("name", CASES)
def test_pandas_polars_identical(name):
    kind, args, opts = CASES[name]()
    ref = plotkit.plot(kind, *args, **opts).to_array()
    got = plotkit.plot(kind, *args[:3], to_polars(args[3]), **opts).to_array()
    assert np.array_equal(ref, got)


def test_styles_and_options():
    data = syn.groups(10)
    a = plotkit.boxplot("Group", "Value", "T", data, style="editorial").to_array()
    b = plotkit.boxplot("Group", "Value", "T", data, style="cobalt").to_array()
    assert not np.array_equal(a, b)
    assert (
        plotkit.boxplot("Group", "Value", "T", data, size="double").fig.get_size_inches()[0] == 7.2
    )
    assert plotkit.boxplot(
        "Group", "Value", "T", data, size=(4, 2)
    ).fig.get_size_inches().tolist() == [4, 2]
    with pytest.raises(TypeError, match="unknown option"):
        plotkit.boxplot("Group", "Value", "T", data, nope=1)
    with pytest.raises(plotkit.RegistryError):
        plotkit.boxplot("Group", "Value", "T", data, style="nope")


def test_data_errors():
    with pytest.raises(plotkit.DataError, match="matches no column"):
        plotkit.boxplot("Missing", "Value", "T", syn.groups(5))
    with pytest.raises(plotkit.DataError, match="x= / y="):
        plotkit.bar("Transcript region", "Usage", "T", syn.region_usage())
    assert plotkit.bar("Transcript region", "Usage", "T", syn.region_usage(), x="region").ax
    with pytest.raises(plotkit.PaletteError):
        plotkit.boxplot("g", "v", "T", {str(i): [1.0, 2.0, 3.0] for i in range(6)})
    with pytest.raises(plotkit.DataError):
        plotkit.continuous("x", "y", "T", [1.0])
    with pytest.raises(plotkit.DataError, match="fit"):
        plotkit.continuous("x", "y", "T", syn.gaussian(), fit="nope")


def test_resolve_labels():
    cols = ["usage", "Time_h", "gene A"]
    assert DataAdapter.resolve("Usage (%)", cols) == "usage"
    assert DataAdapter.resolve("time h", cols) == "Time_h"
    assert DataAdapter.resolve("Gene A", cols) == "gene A"


def test_umap_embedding():
    pytest.importorskip("umap")
    res = plotkit.dim_red(
        "UMAP1", "UMAP2", "T", syn.single_cells(15, 10), hue="cell_type", method="umap"
    )
    assert len(res.ax.collections) == 4 and res.overlaps() == []


def test_dim_red_precomputed_arrays():
    emb = np.random.default_rng(0).normal(size=(30, 2))
    lab = ["a", "b", "c"] * 10
    for data in (emb, emb.tolist()):
        res = plotkit.dim_red("D1", "D2", "T", data, hue=lab)
        assert len(res.ax.collections) == 3
    torch = pytest.importorskip("torch")
    t = torch.tensor(emb, requires_grad=True)
    assert len(plotkit.dim_red("D1", "D2", "T", t, hue=lab).ax.collections) == 3


def test_boxplot_mapping_continuous_variants():
    res = plotkit.boxplot("g", "v", "T", {"a": [1, 2, 3, 4.0], "b": [2, 3, 4, 9.0]}, points=True)
    assert [t.get_text() for t in res.ax.get_xticklabels()] == ["a", "b"]
    for fit in ("normal", None):
        plotkit.continuous("x", None, "T", syn.gaussian(), fit=fit)
    plotkit.survival("t", "s", "T", syn.survival_data(30).drop(columns="group"))
    plotkit.line("time", "response", "T", syn.dose_response().query("dose == 1"))


def test_custom_plot_registration():
    @plotkit.register_plot("flat")
    class Flat(plotkit.BasePlot):
        def draw(self, ax, prepared):
            ax.axhline(0)

    res = plotkit.plot("flat", "x", "y", "T", None)
    assert res.ax.lines and res.overlaps() == []


def test_custom_variant():
    from plotkit.themes import get_variant

    base = get_variant("cobalt")
    plotkit.register_variant(Variantcopy(base))
    assert get_variant("mine").name == "mine"
    assert plotkit.boxplot("Group", "Value", "T", syn.groups(5), style="mine").ax


def Variantcopy(base):
    from dataclasses import replace

    return replace(base, name="mine", bg="#FFFFFF")


def test_import_leaves_pyplot_unloaded():
    import subprocess
    import sys

    code = "import sys, plotkit; assert 'matplotlib.pyplot' not in sys.modules"
    subprocess.run([sys.executable, "-c", code], check=True)
