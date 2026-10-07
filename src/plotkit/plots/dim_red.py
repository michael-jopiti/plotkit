"""Dimensionality-reduction scatter (PCA, UMAP, or any precomputed embedding)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from plotkit.data import DataAdapter
from plotkit.exceptions import DataError
from plotkit.plots.base import BasePlot
from plotkit.plots.registry import register_plot
from plotkit.plots.scatter import MARKERS, add_alpha, point_alpha


def pca(features: np.ndarray, n: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """First ``n`` principal-component scores and the explained variance (%) of all components."""
    x = features - features.mean(0)
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    return u[:, :n] * s[:n], 100 * s**2 / (s**2).sum()


def umap_embedding(
    features: np.ndarray, n_neighbors: int, min_dist: float, seed: int
) -> np.ndarray:
    """2-D UMAP embedding (needs ``pip install plotkit[umap]``)."""
    try:
        import umap
    except ImportError as err:
        raise DataError("method='umap' needs umap-learn: pip install 'plotkit[umap]'") from err
    return np.asarray(
        umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=seed).fit_transform(
            features
        )
    )


@register_plot("dim_red")
class DimRedPlot(BasePlot):
    """2-D embedding colored by ``hue``.

    ``method=None``: ``data`` is already reduced: a table with coordinate columns ``x_name``
    and ``y_name``, or an unnamed ``(n, >=2)`` array (numpy / scikit-learn output, torch tensor,
    cupy / cuML output; first two columns used) with ``hue`` an array-like of labels.
    ``method="pca"`` or ``"umap"``: ``data`` holds features (all numeric columns except
    ``hue``); the embedding is computed here and ``x_name`` / ``y_name`` become the axis
    labels (PCA appends the explained variance, e.g. ``PC1 (53%)``).

    Options: ``hue=None``, ``method=None``, ``n_neighbors=15``, ``min_dist=0.3``, ``seed=0``,
    ``s=10``, ``alpha=None`` (opacity in [0, 1]: a number, a column name, an array with one
    value per point, or a callable ``f(x, y) -> array`` of the embedding coordinates).
    """

    aspect = 1.15
    defaults = {
        "hue": None,
        "method": None,
        "n_neighbors": 15,
        "min_dist": 0.3,
        "seed": 0,
        "s": 10,
        "alpha": None,
    }

    def prepare_data(self) -> pd.DataFrame:
        """Columns ``x``, ``y`` and optionally ``hue`` / ``alpha``."""
        hue, method, alpha = self.opt["hue"], self.opt["method"], self.opt["alpha"]
        if method is None:
            frame = DataAdapter.to_frame(self.data)
            if isinstance(frame.columns, pd.RangeIndex):  # unnamed array: first two columns
                if frame.shape[1] < 2:
                    raise DataError("embedding needs at least 2 columns")
                d = DataAdapter.normalize(None, x=frame[0], y=frame[1], hue=hue).frame
            else:
                d = DataAdapter.normalize(frame, x=self.xcol, y=self.ycol, hue=hue).frame
            return add_alpha(d, alpha, frame)
        frame = DataAdapter.to_frame(self.data)
        skip = [c for c in (hue, alpha) if isinstance(c, str)]
        feats = frame.drop(columns=skip).select_dtypes("number")
        if feats.shape[1] < 2:
            raise DataError("method needs at least 2 numeric feature columns")
        x = feats.to_numpy(dtype=float)
        if method == "pca":
            emb, var = pca(x)
            self.x_name = f"{self.x_name or 'PC1'} ({var[0]:.0f}%)"
            self.y_name = f"{self.y_name or 'PC2'} ({var[1]:.0f}%)"
        elif method == "umap":
            emb = umap_embedding(x, self.opt["n_neighbors"], self.opt["min_dist"], self.opt["seed"])
        else:
            raise DataError(f"method must be None, 'pca' or 'umap', got {method!r}")
        out = pd.DataFrame({"x": emb[:, 0], "y": emb[:, 1]})
        if hue:
            out["hue"] = frame[hue].to_numpy()
        return add_alpha(out, alpha, frame)

    def draw(self, ax: Axes, d: pd.DataFrame) -> None:
        """One color and marker shape per hue level."""
        v, s = self.v, self.opt["s"]
        levels = list(dict.fromkeys(d["hue"])) if "hue" in d else [None]
        pal = v.categorical(len(levels))
        # ponytail: K random chunks per level, drawn round-robin, so no level sits wholly on top
        k = 20
        rng = np.random.default_rng(self.opt["seed"])
        parts = []
        for lvl, color, m in zip(levels, pal.colors, MARKERS, strict=False):
            sub = d if lvl is None else d[d["hue"] == lvl]
            chunks = np.array_split(rng.permutation(len(sub)), k)
            parts.append((lvl, color, m, sub, chunks))
        for c in range(k):
            for lvl, color, m, sub, chunks in parts:
                if not len(chunks[c]):
                    continue
                part = sub.iloc[chunks[c]]
                ax.scatter(
                    part["x"],
                    part["y"],
                    s=s,
                    color=color,
                    marker=m,
                    edgecolors=v.bg,
                    linewidths=0.2,
                    label=None if lvl is None or len(part) == 0 or c else str(lvl),
                    alpha=point_alpha(part),
                )

    def finalize(self, ax: Axes) -> None:
        """Equal scale on both axes, so distances are comparable."""
        ax.set_aspect("equal", adjustable="datalim")
