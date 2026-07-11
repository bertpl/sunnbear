"""The function wrapper owning every per-evaluation concern of a solve.

Applied once by the solve template so individual solvers stay pure algorithm
code: evaluation counting and the budget cap, exclusion of function-body cost
from flop counting, divergence and domain guards, sign normalization, and
optional evaluation history.
"""

import math

from counted_float import PauseFlopCounting

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded
from sunnbear.functions import XFun

# Guard-interval margin: evaluations outside [a - m*(b-a), b + m*(b-a)] count as divergence.
DIVERGENCE_GUARD_MARGIN = 10.0


# ==================================================================================================
#  WrappedFunction
# ==================================================================================================
class WrappedFunction:
    """Wraps a plain ``f(x)`` with counting, budget, guards, sign flip, and history."""

    def __init__(self, f: XFun, a: float, b: float, max_fevals: int, record_history: bool = False) -> None:
        """Wrap `f` for a solve over bracket ``[a, b]`` with the given evaluation budget."""
        self._f = f
        self._guard_lo = a - DIVERGENCE_GUARD_MARGIN * (b - a)
        self._guard_hi = b + DIVERGENCE_GUARD_MARGIN * (b - a)
        self._max_fevals = max_fevals
        self._negate = False
        self.n_fevals = 0
        self.history: list[tuple[float, float]] | None = [] if record_history else None

    # --------------------------------------------------------------------------
    #  Evaluation
    # --------------------------------------------------------------------------
    def __call__(self, x: float) -> float:
        """Evaluate the wrapped function, enforcing budget and guards.

        Raises:
            MaxFevalsExceeded: If the evaluation budget is already exhausted.
            DivergedError: If `x` lies outside the guard interval.
            FunctionDomainError: If the function value is non-finite.
        """
        if self.n_fevals >= self._max_fevals:
            raise MaxFevalsExceeded(f"Function evaluation budget of {self._max_fevals} exhausted.")
        x_plain = float(x)
        if not self._guard_lo <= x_plain <= self._guard_hi:
            raise DivergedError(f"Evaluation at x={x_plain} outside the divergence guard interval.")

        self.n_fevals += 1
        with PauseFlopCounting():
            fx = float(self._f(x_plain))
        if not math.isfinite(fx):
            raise FunctionDomainError(f"Function returned non-finite value {fx} at x={x_plain}.")
        if self._negate:
            fx = -fx
        if self.history is not None:
            self.history.append((x_plain, fx))
        return fx

    # --------------------------------------------------------------------------
    #  Sign normalization
    # --------------------------------------------------------------------------
    def enable_negation(self) -> None:
        """Negate all subsequent (and retroactively, recorded) function values.

        Called once by the solve template when ``f(a) > 0``, so solvers can
        assume ``f(a) <= 0 <= f(b)``.
        """
        self._negate = True
        if self.history is not None:
            self.history = [(x, -fx) for x, fx in self.history]
