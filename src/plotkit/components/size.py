"""Journal figure size presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SizePreset:
    """Figure width in inches with aspect-ratio helpers.

    Parameters
    ----------
    name
        Preset name.
    width
        Figure width in inches.
    """

    name: str
    width: float

    def figsize(self, aspect: float = 4 / 3, height: float | None = None) -> tuple[float, float]:
        """Return ``(width, height)``.

        Parameters
        ----------
        aspect
            Width / height ratio. Ignored when ``height`` is given.
        height
            Explicit height in inches.
        """
        return (self.width, height if height is not None else self.width / aspect)


SINGLE_COLUMN = SizePreset("single", 3.5)
DOUBLE_COLUMN = SizePreset("double", 7.2)
GOLDEN = (1 + 5**0.5) / 2
SQUARE = 1.0
