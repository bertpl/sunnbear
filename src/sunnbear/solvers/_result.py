"""Structured outcome of one solve: status vocabulary and the result record.

The result reports what the solver *did* (evaluations, iterations, flops,
termination status); whether the answer is *correct* is a judgment the
benchmark harness makes separately — a solver never knows the true root.
"""

from dataclasses import dataclass
from enum import Enum

from counted_float import FlopCounts


# ==================================================================================================
#  SolveStatus
# ==================================================================================================
class SolveStatus(Enum):
    """How a solve terminated."""

    CONVERGED = "converged"  # stopping criterion met within budget
    MAX_FEVALS = "max_fevals"  # function-evaluation budget exhausted
    DIVERGED = "diverged"  # left the guard interval around the bracket
    FUNCTION_ERROR = "function_error"  # non-finite function value encountered
    SOLVER_ERROR = "solver_error"  # solver raised — a bug, surfaced not hidden


# ==================================================================================================
#  SolveResult
# ==================================================================================================
@dataclass(frozen=True)
class SolveResult:
    """Measurements and outcome of one solve.

    Attributes:
        x: Best root estimate — the converged solution, or best-so-far on
            abnormal termination.
        status: How the solve terminated.
        n_fevals: Function evaluations consumed (the two initial bracket
            evaluations included).
        n_iters: Iterations, or None for solvers where "iteration" is undefined.
        flop_counts: Full per-operation flop vector of the solver's own
            arithmetic (function-body cost excluded by construction); weighting
            is applied at analysis time.
        history: Chronological ``(x, f(x))`` evaluations if recording was
            requested, else None.
    """

    x: float
    status: SolveStatus
    n_fevals: int
    n_iters: int | None
    flop_counts: FlopCounts
    history: tuple[tuple[float, float], ...] | None = None
