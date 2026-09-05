"""The function wrapper through which a solver evaluates ``f``; owns every per-evaluation concern.

`Solver.solve` wraps the caller's function once and hands the wrapper to the
solver inside the `SolveRun`. Solver implementations never construct one.
"""

import math
from collections.abc import Callable

from counted_float import CountedFloat, PauseFlopCounting

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded

# Half-width of the guard interval, in multiples of the bracket width: an evaluation
# requested outside [a - m*(b-a), b + m*(b-a)] counts as divergence. Generous enough for
# the overshoot of a legitimate open-solver step, tight enough to catch a runaway iterate
# within an iteration or two.
DIVERGENCE_GUARD_MARGIN = 10.0


class WrappedFunction:
    """Wraps ``f(x)`` with evaluation counting, the budget, guards, sign normalization, and history.

    Each call, in order:

    - raises `MaxFevalsExceeded` when this call would exceed `max_fevals`,
      before evaluating anything;
    - raises `DivergedError` when ``x`` lies outside the guard interval;
    - evaluates ``f`` with flop counting paused, so only the solver's own
      arithmetic is counted;
    - raises `FunctionDomainError` on a non-finite value;
    - negates the value when sign normalization is enabled;
    - records ``(x, f(x))`` when history is on;
    - returns the value as a `CountedFloat`, so the solver's arithmetic on it
      is counted.

    The evaluation count includes calls that ended in `FunctionDomainError`: the
    function was evaluated. It excludes calls refused by the budget or the guard.
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
        """Wrap ``f`` for one solve on the bracket ``[a, b]``.

        Args:
            f: The function to find a root of.
            a: Lower end of the bracket; with ``b``, defines the guard interval.
            b: Upper end of the bracket.
            max_fevals: Evaluation budget; the call that would exceed it raises.
            record_history: Whether to keep every ``(x, f(x))`` pair.
        """
        self._f = f
        guard_width = DIVERGENCE_GUARD_MARGIN * (b - a)
        self._guard_lo = a - guard_width
        self._guard_hi = b + guard_width
        self._max_fevals = max_fevals
        self._negate = False
        self.n_fevals = 0
        self.history: list[tuple[float, float]] | None = [] if record_history else None

    def enable_sign_normalization(self) -> None:
        """Negate every value returned from here on, so callers see ``f(a) <= 0 <= f(b)``.

        Values already recorded in the history are negated too: the template
        method decides on normalization only after the endpoint evaluations, and
        the history must show one consistent function.
        """
        self._negate = True
        if self.history is not None:
            self.history = [(x, -fx) for x, fx in self.history]

    def __call__(self, x: float) -> float:
        """Evaluate ``f`` at ``x`` under the wrapper's contract (see the class docstring)."""
        if self.n_fevals >= self._max_fevals:
            raise MaxFevalsExceeded(f"Evaluation budget of {self._max_fevals} function evaluations exhausted.")
        x_plain = float(x)  # guards and the function itself run on plain floats: uncounted, numba-compatible
        if not self._guard_lo <= x_plain <= self._guard_hi:
            raise DivergedError(
                f"Evaluation requested at x={x_plain!r}, outside the guard interval "
                f"[{self._guard_lo!r}, {self._guard_hi!r}]."
            )
        with PauseFlopCounting():
            fx = float(self._f(x_plain))
        self.n_fevals += 1
        if not math.isfinite(fx):
            raise FunctionDomainError(f"f({x_plain!r}) = {fx!r} is not finite.")
        if self._negate:
            fx = -fx
        if self.history is not None:
            self.history.append((x_plain, fx))
        return CountedFloat(fx)
