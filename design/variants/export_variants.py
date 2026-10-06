"""Write src/plotkit/themes/variants.py: variant colors with precomputed gradients.

The gradients come from common.make_gradient (colorspacious, CVD-safe by construction).
Sampling 64 stops keeps the library free of any colorspacious runtime dependency.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, make_gradient  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402

DEFS = {
    "EDITORIAL": dict(
        name="editorial",
        bg="#F2F2F0",
        fg="#111111",
        muted="#555555",
        categorical_hex=("#E35902", "#1C0FF0", "#884FFE", "#7F5E00", "#252424"),
        stops=("#2A0A5E", "#C2187A", "#F2541B", "#FFD23F"),
    ),
    "COBALT": dict(
        name="cobalt",
        bg="#FFFFFF",
        fg="#0B0F1E",
        muted="#4A4F63",
        categorical_hex=("#180CDB", "#CF3B00", "#7C2CFA", "#B28E02", "#0D1226"),
        stops=("#0B1450", "#1F3CFF", "#7FB0FF", "#E3EEFF"),
    ),
}

out = [
    '"""Built-in styles. Gradients are precomputed (see design/variants/export_variants.py)."""',
    "",
    "from plotkit.themes.styled import Variant, register_variant",
    "",
]
for const, d in DEFS.items():
    cmap, scale = make_gradient(d["stops"], d["name"])
    idx = np.linspace(0, cmap.N - 1, 64).round().astype(int)
    hexes = [to_hex(cmap(int(i))).upper() for i in idx]
    lines = ",\n".join(
        "        " + ", ".join(f'"{h}"' for h in hexes[i : i + 6]) for i in range(0, 64, 6)
    )
    out += [
        f"{const} = register_variant(",
        "    Variant(",
        f'        name="{d["name"]}",',
        f'        bg="{d["bg"]}",',
        f'        fg="{d["fg"]}",',
        f'        muted="{d["muted"]}",',
        f"        categorical_hex={d['categorical_hex']!r},".replace("'", '"'),
        f"        # gradient chroma scale needed for CVD safety: {scale:.2f}",
        "        gradient_hex=(",
        lines + ",",
        "        ),",
        "    )",
        ")",
        "",
    ]
(ROOT / "src/plotkit/themes/variants.py").write_text("\n".join(out))
print("wrote variants.py")
