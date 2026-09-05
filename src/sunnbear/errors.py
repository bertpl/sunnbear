"""Exception taxonomy shared across the package.

All sunnbear-raised exceptions derive from `SunnbearError`, so callers can
catch the package's failures with one handler while still discriminating on
the specific subclass.
"""


class SunnbearError(Exception):
    """Base class for all sunnbear-raised exceptions."""


# ==================================================================================================
#  Solve interrupts — control flow inside Solver.solve(), never escaping it
# ==================================================================================================
class SolveInterrupt(SunnbearError):  # noqa: N818 — the name marks a control-flow signal, not an error condition.
    """Base class for the exceptions that stop a solve early.

    The function wrapper raises one of the subclasses from inside an evaluation;
    the `Solver` template method catches every `SolveInterrupt` and maps it to a
    `SolveStatus`, so none of them ever reaches the caller of ``solve()``. Solver
    implementations must let them propagate — swallowing one hides a failed run.
    """


class MaxFevalsExceeded(SolveInterrupt):
    """Raised when an evaluation would exceed the solve's `max_fevals` budget."""


class DivergedError(SolveInterrupt):
    """Raised when a solver asks for an evaluation outside the guard interval around ``[a, b]``."""


class FunctionDomainError(SolveInterrupt):
    """Raised when a function evaluation returns a non-finite value."""


# ==================================================================================================
#  Registry errors
# ==================================================================================================
class UnknownFormulaError(SunnbearError):
    """Raised when a function identity references a formula number not present in the registry."""


class InvalidParamsError(SunnbearError):
    """Raised when a parameter tuple fails its formula's validity criteria."""
