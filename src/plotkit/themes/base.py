"""Abstract theme."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import matplotlib as mpl


class Theme(ABC):
    """A named set of matplotlib rcParams.

    Subclasses implement :meth:`rc_params`. Nothing is applied until
    :meth:`apply` or :meth:`context` is called.
    """

    name: str = "theme"

    @abstractmethod
    def rc_params(self) -> dict[str, Any]:
        """Return the rcParams this theme sets."""

    def apply(self) -> dict[str, Any]:
        """Update global rcParams. Return the previous values (pass to ``reset``)."""
        params = self.rc_params()
        previous = {k: mpl.rcParams[k] for k in params}  # type: ignore[index]
        mpl.rcParams.update(params)  # type: ignore[arg-type]
        return previous

    @contextmanager
    def context(self) -> Iterator[None]:
        """Apply the theme temporarily; previous settings are restored on exit."""
        with mpl.rc_context(self.rc_params()):  # type: ignore[arg-type]
            yield
