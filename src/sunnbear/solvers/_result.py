"""`SolveStatus` and `SolveResult` describe the outcome of one solve."""

from dataclasses import dataclass
from enum import Enum

from counted_float import FlopCounts


# ==================================================================================================
#  SolveStatus
# ==================================================================================================
class SolveStatus(Enum):
    """`SolveStatus` names how a solve ended.

    ``CONVERGED`` means the solver's stopping criterion was met within budget —
    nothing more. Whether the returned ``x`` is correct is judged downstream by
    the benchmark harness, which knows the true root; the solver does not.
    """

    CONVERGED = "converged"
    MAX_FEVALS = "max_fevals"  # the evaluation budget ran out
    DIVERGED = "diverged"  # an evaluation was requested outside the interval WrappedFunction guards around [a, b]
    FUNCTION_ERROR = "function_error"  # the function returned a non-finite value
    SOLVER_ERROR = "solver_error"  # the solver raised — a bug in the solver, recorded, not propagated


# ==================================================================================================
#  SolveResult
# ==================================================================================================
@dataclass(frozen=True)
class SolveResult:
    """A `SolveResult` records what one solve did, as measured by `Solver.solve`.

    The record is closed: every field is shared by all solvers, so the
    benchmark aggregation can read every result whole. A solver with
    diagnostics of its own logs them; it cannot attach them here.

    Attributes:
        x: Root estimate. On an abnormal status, the best estimate so far (for
            a bracketing solver, the last bracket's midpoint).
        n_fevals: Function evaluations performed, the two endpoint evaluations
            included.
        n_iters: Iterations performed, or ``None`` for solvers to which the
            notion does not apply.
        flop_counts: Floating-point operations of the solver's own arithmetic,
            per flop type; function-body cost is excluded.
        history: Every ``(x, f(x))`` evaluated, in order, after sign
            normalization; ``None`` when history was not recorded.
    """

    x: float
    status: SolveStatus
    n_fevals: int
    n_iters: int | None
    flop_counts: FlopCounts
    history: tuple[tuple[float, float], ...] | None
