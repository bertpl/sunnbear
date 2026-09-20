"""This module defines the exceptions that stop a solve early; `SolveInterrupt` says who raises and catches them."""

from sunnbear._core.exceptions import SunnbearError


class SolveInterrupt(SunnbearError):  # noqa: N818 — the name marks a control-flow signal, not an error condition.
    """`SolveInterrupt` is the base class for the exceptions that stop a solve early.

    `WrappedFunction` raises one of the subclasses from inside an evaluation; `Solver.solve`
    catches every `SolveInterrupt` and maps it to a `SolveStatus`, so none of them ever reaches
    the caller of ``solve()``. Solver implementations must let them propagate — catching one hides
    a failed run.
    """


class MaxFevalsExceeded(SolveInterrupt):
    """`WrappedFunction` raises this when an evaluation would exceed the solve's `max_fevals` budget."""


class DivergedError(SolveInterrupt):
    """`WrappedFunction` raises this when a solver asks for an evaluation outside its divergence bounds."""


class FunctionDomainError(SolveInterrupt):
    """`WrappedFunction` raises this when a function evaluation returns a non-finite value."""
