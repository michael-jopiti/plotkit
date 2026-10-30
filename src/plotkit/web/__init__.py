"""Dynamic plots for web pages: plotkit's style as a small SVG renderer in JavaScript.

>>> import plotkit.web
>>> plotkit.web.export("site")  # writes site/plotkit.js with the editorial style baked in
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from plotkit.plots.line import STYLES
from plotkit.themes import Variant, get_variant
from plotkit.themes.proportions import Proportions

__all__ = ["export", "style"]

# dash patterns of the ``line`` plot in multiples of the line width, as SVG dash arrays
_DASHES = {"-": [], "--": [3.7, 1.6], "-.": [6.4, 1.6, 1, 1.6], ":": [1, 1.65]}


def style(name: str | Variant = "editorial") -> dict[str, Any]:
    """Everything the JavaScript renderer needs from a style: colours, sizes (pt), dashes."""
    v = get_variant(name)
    p = Proportions(v.fontsize)
    return {
        "name": v.name,
        "bg": v.bg,
        "fg": v.fg,
        "muted": v.muted,
        "categorical": list(v.categorical().to_hex()),
        "upper_labels": v.upper_labels,
        "font": "Helvetica, 'Nimbus Sans', Arial, 'Liberation Sans', 'DejaVu Sans', sans-serif",
        "fontsize": v.fontsize,
        "tick": p.tick,
        "title_size": v.title_size,
        "hairline": v.hairline,
        "data_lw": p.data_lw,
        "tick_length": p.tick_length,
        "tick_pad": p.tick_pad,
        "dashes": [_DASHES.get(s, [5, 1]) if isinstance(s, str) else [5, 1] for s in STYLES],
    }


def export(directory: str | Path, name: str | Variant = "editorial") -> Path:
    """Write ``plotkit.js`` (renderer plus the style) into ``directory``. Returns its path."""
    src = (Path(__file__).parent / "plotkit.js").read_text()
    out = Path(directory) / "plotkit.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"{src}\nplotkit.style = {json.dumps(style(name), indent=2)};\n")
    return out
