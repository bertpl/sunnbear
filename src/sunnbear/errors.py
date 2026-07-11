"""Exception taxonomy shared across the package.

All sunnbear-raised exceptions derive from `SunnbearError`, so callers can
catch the package's failures with one handler while still discriminating on
the specific subclass.
"""


class SunnbearError(Exception):
    """Base class for all sunnbear-raised exceptions."""


class SolveInterrupt(SunnbearError):  # noqa: N818 — control flow, not an error condition
    """Base class for control-flow exceptions inside a solve.

    Raised by the function wrapper when a run must stop abnormally; the
    `Solver` template method catches every subclass and maps it to a
    `SolveStatus`, so these never escape ``solve()``.
    """


class MaxFevalsExceeded(SolveInterrupt):
    """Raised when a solver attempts to exceed its function-evaluation budget."""


class DivergedError(SolveInterrupt):
    """Raised when a solver requests an evaluation far outside the initial bracket."""


class FunctionDomainError(SolveInterrupt):
    """Raised when a function evaluation returns a non-finite value."""


class UnknownFormulaError(SunnbearError):
    """Raised when a function identity references a formula number not present in the registry."""


class InvalidParamsError(SunnbearError):
    """Raised when a parameter tuple fails its formula's validity criteria."""
