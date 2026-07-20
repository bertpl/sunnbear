"""Exception taxonomy shared across the package.

All sunnbear-raised exceptions derive from `SunnbearError`, so callers can
catch the package's failures with one handler while still discriminating on
the specific subclass.
"""


class SunnbearError(Exception):
    """Base class for all sunnbear-raised exceptions."""


class UnknownFormulaError(SunnbearError):
    """Raised when a function identity references a formula number not present in the registry."""


class InvalidParamsError(SunnbearError):
    """Raised when a parameter tuple fails its formula's validity criteria."""
