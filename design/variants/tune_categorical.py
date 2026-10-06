"""Search categorical colors that satisfy every constraint, keeping each variant's hue families.

For each family (hue fixed from the designer's intended color) it scans lightness,
takes the most saturated in-gamut color, drops those below 3:1 on every page color,
then picks the combination maximizing min(dE / 8, dJ' / 6) across normal vision, three
CVD types and grayscale; ties go to the most chromatic set.
"""

import itertools
import sys
from pathlib import Path

import numpy as np
from colorspacious import cspace_convert
from matplotlib.colors import to_hex, to_rgb

sys.path.insert(0, str(Path(__file__).parent))
from common import CVD, ucs  # noqa: E402
from tests.cvd import contrast  # noqa: E402

FAMILIES = {
    "cobalt": ("#1F3CFF", "#FF5A1F", "#7B2FF7", "#F5C400", "#0B0F1E"),
    "editorial": ("#FF6A13", "#1F3CFF", "#7B2FF7", "#FFC21A", "#111111"),
}
PAGES = {
    "cobalt": ["#FFFFFF"],
    "editorial": ["#F2F2F0", "#FFFFFF"],
}
MIN_CONTRAST = 3.05


def candidates(seed: str, pages: list[str]) -> list[tuple[str, float]]:
    j0, a0, b0 = cspace_convert(to_rgb(seed), "sRGB1", "CAM02-UCS")
    hue, chroma0 = np.arctan2(b0, a0), np.hypot(a0, b0)
    ink = chroma0 < 15
    out = []
    for j in np.linspace(4 if ink else 14, 20 if ink else 64, 17 if ink else 51):
        chromas = np.linspace(0, (0 if chroma0 < 3 else 12) if ink else 70, 48)
        lab = np.stack([np.full_like(chromas, j), chromas * np.cos(hue), chromas * np.sin(hue)], -1)
        rgb = cspace_convert(lab, "CAM02-UCS", "sRGB1")
        ok = ((rgb >= 0) & (rgb <= 1)).all(-1)
        if not ok.any():
            continue
        k = np.flatnonzero(ok).max()
        h = to_hex(rgb[k])
        if all(contrast(h, p) >= MIN_CONTRAST for p in pages):
            out.append((h, float(chromas[k])))
    return out


def score_of(pts, chroma_sum):
    """Return (capped min(dE/8, dJ/6), chroma, dE, dJ) for a (5, conditions, 3) point stack."""
    de = min(
        np.linalg.norm(pts[a] - pts[b], axis=-1).min()
        for a, b in itertools.combinations(range(5), 2)
    )
    dj = np.diff(np.sort(pts[:, 0, 0])).min()
    return min(de / 8, dj / 6, 1.05), chroma_sum, de, dj


def best(name: str, restarts: int = 40):
    """Coordinate descent over the candidate lists with random restarts."""
    rng = np.random.default_rng(0)
    cands = [candidates(s, PAGES[name]) for s in FAMILIES[name]]
    sim = [np.array([[ucs([to_rgb(h)], c)[0] for c in CVD] for h, _ in cs]) for cs in cands]
    chroma = [np.array([c for _, c in cs]) for cs in cands]

    def evaluate(combo):
        pts = np.stack([sim[f][i] for f, i in enumerate(combo)])
        return score_of(pts, sum(chroma[f][i] for f, i in enumerate(combo)))

    top, top_val = None, (-1.0, -1.0)
    for _ in range(restarts):
        combo = [int(rng.integers(len(c))) for c in cands]
        cur = evaluate(combo)
        improved = True
        while improved:
            improved = False
            for f in range(5):
                for i in range(len(cands[f])):
                    trial = combo.copy()
                    trial[f] = i
                    val = evaluate(trial)
                    if val[:2] > cur[:2]:
                        combo, cur, improved = trial, val, True
        if cur[:2] > top_val:
            top, top_val = (combo, cur), cur[:2]
    combo, (score, _, de, dj) = top
    return [cands[f][i][0] for f, i in enumerate(combo)], score, de, dj


if __name__ == "__main__":
    for name in FAMILIES:
        hexes, score, de, dj = best(name)
        print(f"{name}: {hexes}  score={score:.2f} dE={de:.1f} dJ={dj:.1f}")
