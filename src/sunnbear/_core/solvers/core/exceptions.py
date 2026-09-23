"""This module defines the exceptions that stop a solve early; `SolveException` says who raises and catches them."""

from sunnbear._core.exceptions import SunnbearError


class SolveException(SunnbearError):  # noqa: N818 — the name marks a control-flow signal, not an error condition.
    """`SolveException` is the base class for the exceptions that stop a solve early.

    `WrappedFunction` raises one of the subclasses from inside an evaluation; `Solver.solve`
    catches every `SolveException` and maps it to a `SolveStatus`, so none of them ever reaches
    the caller of ``solve()``. Solver implementations must let them propagate — catching one hides
    a failed run.
    """


class MaxFevalsExceeded(SolveException):
    """`WrappedFunction` raises this when an evaluation would exceed the solve's `max_fevals` budget."""


class DivergedError(SolveException):
    """`WrappedFunction` raises this when a solver asks for an evaluation at a non-finite ``x``."""


class FunctionDomainError(SolveException):
    """`WrappedFunction` raises this when ``f`` raises or returns a non-finite value.

    Attributes:
        x: Where the evaluation failed; `Solver.solve` reads it to tell a function error inside
            the interval from a solver that diverged into a region where ``f`` fails.
    """

    def __init__(self, x: float, message: str) -> None:
        """Record where the evaluation failed, then behave as a plain exception with ``message``."""
        super().__init__(message)
        self.x = x


class UnknownSolverConfigError(SunnbearError):
    """Raised when a ``solver_id`` names no registered solver config."""
