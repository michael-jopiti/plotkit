import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    assert len(res.ax.get_legend_handles_labels()[1]) == 4 and res.overlaps() == []


def test_dim_red_precomputed_arrays():
    emb = np.random.default_rng(0).normal(size=(30, 2))
    lab = ["a", "b", "c"] * 10
    for data in (emb, emb.tolist()):
        res = plotkit.dim_red("D1", "D2", "T", data, hue=lab)
        assert len(res.ax.get_legend_handles_labels()[1]) == 3
    torch = pytest.importorskip("torch")
    t = torch.tensor(emb, requires_grad=True)
    assert len(plotkit.dim_red("D1", "D2", "T", t, hue=lab).ax.get_legend_handles_labels()[1]) == 3


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


def test_alpha_option():
    emb = np.random.default_rng(0).normal(size=(30, 2))
    lab = ["a", "b", "c"] * 10
    per_point = np.linspace(0.1, 1, 30)
    for alpha in (0.3, per_point, lambda x, y: np.clip(np.hypot(x, y) / 3, 0, 1)):
        res = plotkit.dim_red("D1", "D2", "T", emb, hue=lab, alpha=alpha)
        assert res.ax.collections[0].get_alpha() is not None
    df = syn.expression(20).assign(a=np.linspace(0.1, 1, 60))
    res = plotkit.scatter("gene_0", "gene_1", "T", df, hue="group", alpha="a")
    assert sum(len(c.get_alpha()) for c in res.ax.collections) == 60
    with pytest.raises(plotkit.exceptions.DataError):
        plotkit.dim_red("D1", "D2", "T", emb, alpha=[0.5] * 3)


def test_subtitle_and_caption():
    base = plotkit.scatter("gene_0", "gene_1", "T", syn.expression(), hue="group")
    assert not base.ax.texts and base.fig._supxlabel is None
    res = plotkit.scatter(
        "gene_0",
        "gene_1",
        "T",
        syn.expression(),
        hue="group",
        subtitle="n = 60\nthree groups",
        caption="A long caption " * 12,
    )
    assert res.overlaps() == []
    assert res.fig._supxlabel.get_text().count("\n") >= 1


@pytest.mark.parametrize("kind", ["scatter", "dim_red"])
def test_marginals(kind):
    plain = getattr(plotkit, kind)("gene_0", "gene_1", "T", syn.expression(), hue="group")
    res = getattr(plotkit, kind)(
        "gene_0", "gene_1", "T", syn.expression(), hue="group", marginals=True, subtitle="s"
    )
    top, right = res.fig.axes[1:]
    assert len(plain.fig.axes) == 1 and len(res.fig.axes) == 3
    assert top.get_xlim() == res.ax.get_xlim() and right.get_ylim() == res.ax.get_ylim()
    assert len(top.lines) == 3 and len(right.lines) == 3  # one KDE per hue level
    assert res.overlaps() == []


def test_marginals_need_a_subplot():
    fig = plt.figure()
    with pytest.raises(plotkit.DataError):
        plotkit.scatter(
            "gene_0", "gene_1", "T", syn.expression(), ax=fig.add_axes([0, 0, 1, 1]), marginals=True
        )


def test_option_validation():
    data = syn.groups(5)
    with pytest.raises(ValueError, match="size"):
        plotkit.boxplot("Group", "Value", "T", data, size="triple")
    with pytest.raises(plotkit.DataError, match="error"):
        plotkit.bar("Region", "Usage", "T", syn.region_usage(), error="se")
    with pytest.raises(plotkit.DataError, match="order"):
        plotkit.boxplot("Group", "Value", "T", data, order=["nope"])
    with pytest.raises(plotkit.DataError, match="group column"):
        plotkit.survival("t", "s", "T", syn.survival_data(), group="grp")
    with pytest.raises(plotkit.DataError, match="hue"):
        plotkit.dim_red("a", "b", "T", syn.expression(), method="pca", hue=[0, 1])


def test_heatmap_constant_row_is_finite():
    df = pd.DataFrame({"gene": ["a", "b"], "s1": [1.0, 3.0], "s2": [1.0, 4.0], "s3": [1.0, 5.0]})
    res = plotkit.heatmap("Sample", "Gene", "T", df)
    assert np.isfinite(res.ax.images[0].get_array()).all()


def test_save_keeps_dots_in_name(tmp_path):
    res = plotkit.continuous("x", "y", "T", syn.gaussian())
    assert res.save(tmp_path / "fig_0.5", formats=("png",))[0].name == "fig_0.5.png"
    assert res.save(tmp_path / "fig.png", formats=("png",))[0].name == "fig.png"


@pytest.mark.parametrize("name", CASES)
@pytest.mark.parametrize("opts", [{"style": "cobalt"}, {"size": "double"}])
def test_no_overlap_across_styles_and_sizes(name, opts):
    kind, args, kw = CASES[name]()
    assert plotkit.plot(kind, *args, **kw, **opts).overlaps() == []
