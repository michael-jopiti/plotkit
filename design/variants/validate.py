"""Validate every palette of every variant against the non-negotiable constraints."""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import CVD, luminance, min_de, monotonic, ucs  # noqa: E402
from tests.cvd import contrast  # noqa: E402

from plotkit.themes.styled import Variant  # noqa: E402

MIN_TEXT_CONTRAST = 4.5
MIN_MARK_CONTRAST = 3.0
MIN_CATEGORICAL_DE = 8.0
MIN_CATEGORICAL_GRAY_DJ = 6.0
MIN_DISCRETE_DE = 6.0


@dataclass
class Check:
    variant: str
    scope: str
    name: str
    value: float | bool
    threshold: str
    ok: bool

    def line(self) -> str:
        v = f"{self.value:.2f}" if isinstance(self.value, float) else str(self.value)
        return f"{'PASS' if self.ok else 'FAIL'}  {self.variant:9s} {self.scope:22s} {self.name:34s} {v:>7s}  ({self.threshold})"


def validate(v: Variant) -> list[Check]:
    out: list[Check] = []

    def add(scope, name, value, threshold, ok):
        out.append(Check(v.name, scope, name, value, threshold, bool(ok)))

    for bg in dict.fromkeys([v.bg, "#FFFFFF"]):
        scope = f"on {bg}"
        for label, color in (("text", v.fg), ("tick labels, axes", v.muted)):
            c = contrast(color, bg)
            add(
                scope,
                f"{label} contrast",
                float(c),
                f">= {MIN_TEXT_CONTRAST}",
                c >= MIN_TEXT_CONTRAST,
            )
        cat = v.categorical()
        worst = min(cat.colors, key=lambda c: contrast(_hex(c), bg))
        c = contrast(_hex(worst), bg)
        add(
            scope,
            f"categorical worst contrast {_hex(worst)}",
            float(c),
            f">= {MIN_MARK_CONTRAST}",
            c >= MIN_MARK_CONTRAST,
        )

    cat = v.categorical()
    de = min_de(cat.colors)
    add(
        "categorical",
        "min dE, normal + 3 CVD",
        float(de),
        f">= {MIN_CATEGORICAL_DE}",
        de >= MIN_CATEGORICAL_DE,
    )
    j = np.sort(ucs(cat.colors)[:, 0])
    dj = float(np.diff(j).min())
    add(
        "categorical",
        "min dJ' grayscale",
        dj,
        f">= {MIN_CATEGORICAL_GRAY_DJ}",
        dj >= MIN_CATEGORICAL_GRAY_DJ,
    )

    def ramp_checks(scope, rgb):
        add(
            scope,
            "lightness monotonic (normal)",
            monotonic(ucs(rgb)[:, 0]),
            "strict",
            monotonic(ucs(rgb)[:, 0]),
        )
        for cvd in CVD[1:]:
            m = monotonic(ucs(rgb, cvd)[:, 0])
            add(scope, f"lightness monotonic ({cvd['cvd_type']})", m, "strict", m)
        g = monotonic(luminance(rgb))
        add(scope, "luminance monotonic (grayscale)", g, "strict", g)

    ramp_checks("continuous", v.continuous().colors)
    for n in range(3, 10):
        pal = v.discrete(n)
        ramp_checks(f"discrete n={n}", pal.colors)
        d = min_de(pal.colors)
        add(
            f"discrete n={n}",
            "min dE, normal + 3 CVD",
            float(d),
            f">= {MIN_DISCRETE_DE}",
            d >= MIN_DISCRETE_DE,
        )
    return out


def _hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(int(round(c * 255)) for c in rgb))


def report(variants: list[Variant]) -> tuple[str, int]:
    checks = [c for v in variants for c in validate(v)]
    lines = [c.line() for c in checks]
    fails = [c for c in checks if not c.ok]
    lines.append(f"\n{len(checks) - len(fails)}/{len(checks)} checks passed")
    return "\n".join(lines), len(fails)


if __name__ == "__main__":
    from plotkit.themes.variants import COBALT, EDITORIAL

    text, n_fail = report([EDITORIAL, COBALT])
    print(text)
