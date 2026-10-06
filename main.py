"""Gallery: one call per plot. Usage: ``uv run python main.py [editorial|cobalt]``."""

import sys

import plotkit
from plotkit import synthetic as syn

kw = {"style": sys.argv[1] if len(sys.argv) > 1 else "editorial"}
out = f"examples/output/{kw['style']}"


def show(name, result):
    print(f"{name}: overlaps {result.overlaps()}")
    result.save(f"{out}/{name}")


gauss = syn.gaussian(2, 0.5)
show("gaussian", plotkit.continuous("Value (a.u.)", "Density", "Gaussian", gauss, **kw))
show("boxplot", plotkit.boxplot("Group", "Value (a.u.)", "Quantiles", syn.groups(), **kw))
show(
    "barplot",
    plotkit.bar("Region", "Usage (%)", "Region usage", syn.region_usage(), hue="condition", **kw),
)
show("pca", plotkit.dim_red("PC1", "PC2", "PCA", syn.expression(), hue="group", method="pca", **kw))
show(
    "umap",
    plotkit.dim_red(
        "UMAP1", "UMAP2", "UMAP", syn.single_cells(), hue="cell_type", method="umap", **kw
    ),
)
show(
    "volcano",
    plotkit.volcano("log2 fold change", "-log10 p", "Volcano", syn.differential_expression(), **kw),
)
show(
    "survival",
    plotkit.survival(
        "Time (months)", "Survival probability", "Survival", syn.survival_data(), **kw
    ),
)
show("heatmap", plotkit.heatmap("Samples", "Genes", "Expression", syn.expression_matrix(), **kw))
show(
    "dose_response",
    plotkit.line(
        "Time (h)", "Response", "Dose response", syn.dose_response(), hue="dose", ordered=True, **kw
    ),
)
show(
    "scatter",
    plotkit.scatter("gene_0", "gene_1", "Scatter", syn.expression(), color="gene_2", **kw),
)
