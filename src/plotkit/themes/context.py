"""Explicit global application of a theme."""

from __future__ import annotations

from typing import Any

import matplotlib as mpl

from plotkit.themes.base import Theme
from plotkit.themes.registry import get_theme


def apply(theme: Theme | str = "publication") -> dict[str, Any]:
    """Apply ``theme`` (instance or registered name) globally.

    Returns
    -------
    dict
        Previous values of the touched rcParams; pass to :func:`reset` to undo.
    """
    return (get_theme(theme) if isinstance(theme, str) else theme).apply()


def reset(previous: dict[str, Any] | None = None) -> None:
    """Restore ``previous`` rcParams, or matplotlib defaults when omitted."""
    if previous is None:
        mpl.rcdefaults()
    else:
        mpl.rcParams.update(previous)  # type: ignore[arg-type]
