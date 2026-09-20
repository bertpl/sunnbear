"""`WrappedFunction` wraps ``f`` for one solve; every evaluation goes through it.

Each call runs the checks documented on the class, in order.

`Solver.solve` builds one per solve and hands it over inside the `SolverState`;
solver implementations never construct one.
"""

import math
from collections.abc import Callable

from counted_float import CountedFloat, PauseFlopCounting

from .exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded

# The divergence bounds are the bracket widened on each side by this multiple of its width; an evaluation
# requested outside them counts as divergence.
#
# The factor balances two needs: generous enough to tolerate the overshoot of a legitimate step of a
# non-bracketing solver, but finite enough to detect a divergent iterate within a few iterations. A
# non-bracketing solver may legitimately step far outside the bracket and return, so the factor errs
# toward tolerance.
DIVERGENCE_GUARD_WIDTH_FACTOR = 1e3


class WrappedFunction:
    """A `WrappedFunction` wraps ``f`` for one solve; each call runs the checks below.

    A call:

    - raises `MaxFevalsExceeded` when the call would exceed ``max_fevals``,
      before evaluating anything;
    - raises `DivergedError` when ``x`` lies outside the divergence bounds;
    - evaluates ``f`` with flop counting paused, so only the solver's own
      arithmetic is counted;
    - raises `FunctionDomainError` on a non-finite value;
    - appends ``(x, f(x))`` to the history when history is on, so the history is the caller's ``f`` as
      evaluated, in call order;
    - returns the value as a `CountedFloat`, so the solver's arithmetic on it
      is counted.

    The evaluation count includes calls that ended in `FunctionDomainError`,
    since the function was evaluated; the count excludes calls refused by the
    budget or the divergence bounds.
    """

    def __init__(
        self,
        f: Callable[[float], float],
        a: float,
        b: float,
        *,
        max_fevals: int,
        record_history: bool,
    ) -> None:
        """Wrap ``f`` for one solve; the divergence bounds are derived from ``[a, b]``."""
        self._f = f
        self._divergence_lb = a - DIVERGENCE_GUARD_WIDTH_FACTOR * (b - a)
        self._divergence_ub = b + DIVERGENCE_GUARD_WIDTH_FACTOR * (b - a)
        self._max_fevals = max_fevals
        self.n_fevals = 0
        self.history: list[tuple[float, float]] | None = [] if record_history else None

    def __call__(self, x: float) -> float:
        """Evaluate ``f`` at ``x``: refuse it past the budget or the divergence bounds, and reject a non-finite value.

        Returns:
            The value as a `CountedFloat`, so the solver's arithmetic on it is counted.
        """
        if self.n_fevals >= self._max_fevals:
            raise MaxFevalsExceeded(f"Evaluation budget of {self._max_fevals} function evaluations exhausted.")
        x_plain = float(x)  # The checks and f itself run on plain floats: uncounted, and numba-compatible.
        if not self._divergence_lb <= x_plain <= self._divergence_ub:
            raise DivergedError(
                f"Evaluation requested at x={x_plain!r}, outside the divergence bounds "
                f"[{self._divergence_lb!r}, {self._divergence_ub!r}]."
            )
        with PauseFlopCounting():
            fx = float(self._f(x_plain))
        self.n_fevals += 1
        if not math.isfinite(fx):
            raise FunctionDomainError(f"f({x_plain!r}) = {fx!r} is not finite.")
        if self.history is not None:
            self.history.append((x_plain, fx))
        return CountedFloat(fx)
