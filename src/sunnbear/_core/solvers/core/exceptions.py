"""This module defines the exceptions that stop a solve early.

`Solver.solve` catches every `SolveInterrupt` and maps it to a `SolveStatus`, so none of them ever
reaches the caller of ``solve()``.
"""

from sunnbear._core.exceptions import SunnbearError


class SolveInterrupt(SunnbearError):  # noqa: N818 — the name marks a control-flow signal, not an error condition.
    """Base class for the exceptions that stop a solve early.

    `WrappedFunction` raises one of the subclasses from inside an evaluation;
    the `Solver` template method catches every `SolveInterrupt` and maps it to a
    `SolveStatus`, so none of them ever reaches the caller of ``solve()``. Solver
    implementations must let them propagate — catching one hides a failed run.
    """


class MaxFevalsExceeded(SolveInterrupt):
    """Raised when an evaluation would exceed the solve's `max_fevals` budget."""


class DivergedError(SolveInterrupt):
    """Raised when a solver asks for an evaluation outside the interval that `WrappedFunction` guards."""


class FunctionDomainError(SolveInterrupt):
    """Raised when a function evaluation returns a non-finite value."""
