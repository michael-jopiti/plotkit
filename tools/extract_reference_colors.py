"""Print dominant colors of the reference images (k-means). A starting point only."""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

ROOT = Path(__file__).parents[1]
K = 7


def contrast_vs_white(rgb: np.ndarray) -> float:
    c = rgb / 255
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(1.05 / (c @ [0.2126, 0.7152, 0.0722] + 0.05))


def dominant(path: Path, k: int = K) -> list[tuple[str, float, float]]:
    img = Image.open(path).convert("RGBA")
    flat = Image.new("RGBA", img.size, "white")
    flat.alpha_composite(img)
    rgb = flat.convert("RGB")
    rgb.thumbnail((160, 160))
    px = np.asarray(rgb, dtype=float).reshape(-1, 3)
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(px)
    share = np.bincount(km.labels_, minlength=k) / len(px)
    rows = [
        ("#{:02X}{:02X}{:02X}".format(*(int(round(v)) for v in c)), s, contrast_vs_white(c))
        for c, s in zip(km.cluster_centers_, share, strict=True)
    ]
    return sorted(rows, key=lambda r: -r[1])


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "design" / "references"
    for p in sorted(folder.glob("*.png")):
        print(f"\n{p.name}")
        for hex_, share, contrast in dominant(p):
            print(f"  {hex_}  {share:6.1%}  contrast vs white {contrast:4.1f}:1")
