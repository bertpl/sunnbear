"""Per-solve mutable context handed to solver implementations.

Solver instances themselves are immutable configuration; everything that
changes during one solve lives here, so instances can be reused and shared
freely across runs.
"""

from dataclasses import dataclass

from ._wrapped_function import WrappedFunction


# ==================================================================================================
#  SolveRun
# ==================================================================================================
@dataclass
class SolveRun:
    """State of one solve in progress.

    Attributes:
        f: The wrapped function; all evaluations go through it.
        a: Lower bracket endpoint (sign-normalized: ``f(a) <= 0``).
        b: Upper bracket endpoint (``f(b) >= 0``).
        fa: Function value at `a`.
        fb: Function value at `b`.
        xtol: Requested x-tolerance.
        n_iters: Iterations marked so far, or None if the solver does not
            report iterations.
        best_x: Best root estimate so far — reported when the run terminates
            abnormally.
    """

    f: WrappedFunction
    a: float
    b: float
    fa: float
    fb: float
    xtol: float
    n_iters: int | None = None
    best_x: float = 0.0

    def mark_iteration(self) -> None:
        """Record the completion of one iteration."""
        self.n_iters = (self.n_iters or 0) + 1
