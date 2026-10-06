"""Themes: matplotlib rcParams bundles applied explicitly."""

from plotkit.themes.base import Theme
from plotkit.themes.context import apply, reset
from plotkit.themes.publication import PublicationTheme
from plotkit.themes.registry import get_theme, register_theme

__all__ = ["PublicationTheme", "Theme", "apply", "get_theme", "register_theme", "reset"]
