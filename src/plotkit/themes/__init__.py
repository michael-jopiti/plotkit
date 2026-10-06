"""Themes: matplotlib rcParams bundles applied explicitly."""

from plotkit.themes import variants as _variants  # noqa: F401  (registers built-in styles)
from plotkit.themes.base import Theme
from plotkit.themes.context import apply, reset
from plotkit.themes.publication import PublicationTheme
from plotkit.themes.registry import get_theme, register_theme
from plotkit.themes.styled import StyledTheme, Variant, get_variant, register_variant

__all__ = [
    "PublicationTheme",
    "StyledTheme",
    "Theme",
    "Variant",
    "apply",
    "get_theme",
    "get_variant",
    "register_theme",
    "register_variant",
    "reset",
]
