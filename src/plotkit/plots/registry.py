"""Plot registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from plotkit.plots.base import BasePlot
from plotkit.registry import Registry

plots: Registry[type[BasePlot]] = Registry("plot", "plotkit.plots")
P = TypeVar("P", bound=type[BasePlot])


def register_plot(name: str, *, overwrite: bool = False) -> Callable[[P], P]:
    """Class decorator: make a :class:`BasePlot` subclass available as ``plot(name, ...)``."""

    def deco(cls: P) -> P:
        cls.name = name
        plots.register(name, cls, overwrite=overwrite)
        return cls

    return deco
