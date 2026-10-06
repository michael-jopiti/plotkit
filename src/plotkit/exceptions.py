"""Exception hierarchy for plotkit."""


class PlotkitError(Exception):
    """Base class for all plotkit errors."""


class PaletteError(PlotkitError, ValueError):
    """Invalid palette request (bad size, unknown name)."""


class ThemeError(PlotkitError, RuntimeError):
    """Theme cannot be applied (e.g. LaTeX not installed)."""


class DataError(PlotkitError, TypeError):
    """Input data cannot be converted or is missing columns."""


class RegistryError(PlotkitError, KeyError):
    """Unknown or duplicate registry entry."""
