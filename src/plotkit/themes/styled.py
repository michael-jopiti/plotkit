"""Styles: a page color, ink, three palettes and a theme, bundled as a Variant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap

from plotkit.palettes.categorical import CategoricalPalette
from plotkit.palettes.continuous import ContinuousPalette
from plotkit.palettes.discrete import DiscretePalette
from plotkit.palettes.registry import register_palette
from plotkit.registry import Registry
from plotkit.themes.publication import PublicationTheme
from plotkit.themes.registry import register_theme


class StyledTheme(PublicationTheme):
    """PublicationTheme with a colored page, ink text, bold display titles, hairline axes."""

    def __init__(self, variant: Variant, background: str | None = None) -> None:
        super().__init__(fontsize=variant.fontsize)
        self.variant = variant
        self.background = background or variant.bg
        self.name = variant.name

    def rc_params(self) -> dict[str, Any]:
        """Return the rcParams for this theme."""
        v, bg = self.variant, self.background
        rc = super().rc_params()
        rc.update(
            {
                "figure.facecolor": bg,
                "axes.facecolor": bg,
                "savefig.facecolor": bg,
                "text.color": v.fg,
                "axes.labelcolor": v.fg,
                "axes.edgecolor": v.fg,
                "axes.titlecolor": v.fg,
                "xtick.color": v.fg,
                "ytick.color": v.fg,
                "xtick.labelcolor": v.muted,
                "ytick.labelcolor": v.muted,
                "legend.labelcolor": v.fg,
                "axes.titleweight": "bold",
                "axes.titlesize": v.title_size,
                "axes.titlepad": 9.0,
                "axes.linewidth": v.hairline,
                "xtick.major.width": v.hairline,
                "ytick.major.width": v.hairline,
                "patch.linewidth": v.hairline,
                "grid.color": v.muted,
                "grid.alpha": 0.25,
                "grid.linewidth": v.hairline,
                "hatch.linewidth": v.hairline,
                "axes.prop_cycle": cycler(color=v.categorical().to_hex()),
            }
        )
        return rc


@dataclass(frozen=True)
class Variant:
    """A style: page and ink colors, three palettes, theme.

    Parameters
    ----------
    name
        Registry name.
    bg, fg, muted
        Page color, ink color, secondary text/axis-label color (all contrast-checked).
    categorical_hex
        Unordered colors in priority order (3:1 contrast on the page).
    gradient_hex
        Densely sampled gradient with monotonic lightness (dark to light).
    discrete_span
        Part of the gradient used for ordered discrete steps.
    upper_labels
        Uppercase axis-label names (units keep their case).
    """

    name: str
    bg: str
    fg: str
    muted: str
    categorical_hex: tuple[str, ...]
    gradient_hex: tuple[str, ...]
    discrete_span: tuple[float, float] = (0.0, 0.9)
    upper_labels: bool = True
    fontsize: float = 7.0
    title_size: float = 11.0
    hairline: float = 0.5

    def theme(self, background: str | None = None) -> StyledTheme:
        """Theme on the variant's page color, or on ``background`` (e.g. ``"#FFFFFF"``)."""
        return StyledTheme(self, background)

    def categorical(self, n: int | None = None) -> CategoricalPalette:
        """Unordered palette (up to ``len(categorical_hex)`` colors)."""
        return CategoricalPalette(n, colors=self.categorical_hex, name=self.name)

    def continuous(self) -> ContinuousPalette:
        """Smooth gradient with monotonic lightness."""
        cmap = LinearSegmentedColormap.from_list(self.name, list(self.gradient_hex), N=256)
        return ContinuousPalette(cmap)

    def discrete(self, n: int = 5) -> DiscretePalette:
        """``n`` ordered steps (3 to 9) sampled from the gradient."""
        return DiscretePalette(n, self.continuous().cmap, self.discrete_span)


variants: Registry[Variant] = Registry("style", "plotkit.styles")


def register_variant(variant: Variant, *, overwrite: bool = False) -> Variant:
    """Register a style: its theme and its three palettes become available by name.

    This single call is the whole extension: define a :class:`Variant`, register it.
    """
    v = variant
    variants.register(v.name, v, overwrite=overwrite)
    register_theme(v.name, v.theme, overwrite=overwrite)
    register_palette(f"{v.name}-categorical", lambda n: v.categorical(n), overwrite=overwrite)
    register_palette(
        f"{v.name}-discrete", lambda n: v.discrete(5 if n is None else n), overwrite=overwrite
    )
    register_palette(f"{v.name}-continuous", lambda n: v.continuous(), overwrite=overwrite)
    return v


def get_variant(style: str | Variant) -> Variant:
    """Return the registered style called ``style`` (instances pass through)."""
    return style if isinstance(style, Variant) else variants.get(style)
