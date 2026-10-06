"""Synthetic datasets for demos and tests. Every function returns pandas objects / arrays."""

from __future__ import annotations

from math import erfc

import numpy as np
import pandas as pd


def gaussian(mu: float = 0.0, sigma: float = 1.0, n: int = 5000, seed: int = 0) -> np.ndarray:
    """``n`` samples from N(mu, sigma)."""
    return np.random.default_rng(seed).normal(mu, sigma, n)


def groups(n: int = 60, seed: int = 0) -> pd.DataFrame:
    """Columns ``group`` (A, B, C) and ``value``; C is skewed."""
    rng = np.random.default_rng(seed)
    vals = [rng.normal(10, 2, n), rng.normal(13, 3, n), rng.lognormal(2.5, 0.3, n)]
    return pd.DataFrame({"group": np.repeat(["A", "B", "C"], n), "value": np.concatenate(vals)})


def region_usage(n_rep: int = 6, seed: int = 0) -> pd.DataFrame:
    """Columns ``condition``, ``region``, ``usage`` (%): CDS / Intron / 3'UTR, control vs cancer."""
    rng = np.random.default_rng(seed)
    means = {"Control": [62, 28, 10], "Cancer": [48, 36, 16]}
    rows = [
        (c, r, v)
        for c, ms in means.items()
        for r, m in zip(["CDS", "Intron", "3'UTR"], ms, strict=True)
        for v in rng.normal(m, 0.08 * m, n_rep)
    ]
    return pd.DataFrame(rows, columns=["condition", "region", "usage"])


def expression(n_per: int = 50, n_features: int = 8, seed: int = 0) -> pd.DataFrame:
    """Features ``gene_0..`` plus ``group`` (Control, Treated A, Treated B): three clusters."""
    rng = np.random.default_rng(seed)
    names = ["Control", "Treated A", "Treated B"]
    centers = rng.normal(0, 2.0, (3, n_features))
    x = np.vstack([c + rng.normal(0, 1.0, (n_per, n_features)) for c in centers])
    df = pd.DataFrame(x, columns=[f"gene_{i}" for i in range(n_features)])
    df["group"] = np.repeat(names, n_per)
    return df


def single_cells(n_per: int = 100, n_features: int = 30, seed: int = 0) -> pd.DataFrame:
    """Features ``gene_0..`` plus ``cell_type`` (T cell, B cell, Monocyte, NK cell)."""
    rng = np.random.default_rng(seed)
    names = ["T cell", "B cell", "Monocyte", "NK cell"]
    centers = rng.normal(0, 3.0, (4, n_features))
    x = np.vstack([c + rng.normal(0, 1.0, (n_per, n_features)) for c in centers])
    df = pd.DataFrame(x, columns=[f"gene_{i}" for i in range(n_features)])
    df["cell_type"] = np.repeat(names, n_per)
    return df


def differential_expression(n: int = 3000, seed: int = 0) -> pd.DataFrame:
    """Columns ``gene``, ``log2fc``, ``pvalue``; about 10% of genes truly change."""
    rng = np.random.default_rng(seed)
    lfc = rng.normal(0, 0.35, n)
    hit = rng.choice(n, n // 10, replace=False)
    lfc[hit] += rng.choice([-1, 1], len(hit)) * rng.uniform(0.8, 2.5, len(hit))
    z = np.abs(lfc / rng.uniform(0.15, 0.45, n))
    p = np.array([erfc(v / 2**0.5) for v in z])
    return pd.DataFrame({"gene": [f"G{i}" for i in range(n)], "log2fc": lfc, "pvalue": p})


def survival_data(n: int = 80, seed: int = 0) -> pd.DataFrame:
    """Columns ``time`` (months), ``event`` (1 = event, 0 = censored), ``group`` (Low/High risk)."""
    rng = np.random.default_rng(seed)
    frames = []
    for name, scale in (("Low risk", 40.0), ("High risk", 18.0)):
        t, c = rng.exponential(scale, n), rng.uniform(5, 60, n)
        frames.append(
            pd.DataFrame({"time": np.minimum(t, c), "event": (t <= c).astype(int), "group": name})
        )
    return pd.concat(frames, ignore_index=True)


def expression_matrix(n_per: int = 10, seed: int = 0) -> pd.DataFrame:
    """Wide table: ``gene`` label column, ``Control 1..`` and ``Treated 1..`` sample columns."""
    rng = np.random.default_rng(seed)
    genes = [
        "TP53",
        "MYC",
        "EGFR",
        "KRAS",
        "BRCA1",
        "PTEN",
        "CDK4",
        "RB1",
        "VEGFA",
        "STAT3",
        "MKI67",
        "CCND1",
    ]
    base = rng.normal(0, 1, (len(genes), 2 * n_per))
    base[:, n_per:] += np.r_[np.full(6, 1.2), np.full(6, -1.2)][:, None]
    cols = [f"Control {i + 1}" for i in range(n_per)] + [f"Treated {i + 1}" for i in range(n_per)]
    df = pd.DataFrame(base, columns=cols)
    df.insert(0, "gene", genes)
    return df


def dose_response(seed: int = 0) -> pd.DataFrame:
    """Columns ``time`` (h), ``response``, ``dose`` (0.1 to 1000 nM)."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 10, 60)
    rows = [
        pd.DataFrame(
            {
                "time": t,
                "response": 1 - np.exp(-t * d**0.4 / 10) + rng.normal(0, 0.01, t.size),
                "dose": d,
            }
        )
        for d in (0.1, 1, 10, 100, 1000)
    ]
    return pd.concat(rows, ignore_index=True)
