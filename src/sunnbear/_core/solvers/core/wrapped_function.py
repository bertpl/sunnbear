"""`WrappedFunction` wraps ``f`` for one solve; every evaluation goes through it.

Each call runs the checks documented on the class, in order.

`Solver.solve` builds one per solve and hands it over inside the `SolveRun`;
solver implementations never construct one.
"""

import math
from collections.abc import Callable

from counted_float import CountedFloat, PauseFlopCounting

from .exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded

# The guard interval is the bracket widened on each side by this multiple of its width; an evaluation
# requested outside the guard interval counts as divergence.
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
    - raises `DivergedError` when ``x`` lies outside the guard interval;
    - evaluates ``f`` with flop counting paused, so only the solver's own
      arithmetic is counted;
    - raises `FunctionDomainError` on a non-finite value;
    - negates the value when sign normalization is enabled;
    - records ``(x, f(x))`` when history is on;
    - returns the value as a `CountedFloat`, so the solver's arithmetic on it
      is counted.

    The evaluation count includes calls that ended in `FunctionDomainError`,
    since the function was evaluated; the count excludes calls refused by the
    budget or the guard.
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
        """Wrap ``f`` for one solve; the guard interval is derived from ``[a, b]``."""
        self._f = f
        guard_width = DIVERGENCE_GUARD_WIDTH_FACTOR * (b - a)
        self._guard_lo = a - guard_width
        self._guard_hi = b + guard_width
        self._max_fevals = max_fevals
        self._is_sign_normalized = False
        self.n_fevals = 0
        self.history: list[tuple[float, float]] | None = [] if record_history else None

    def enable_sign_normalization(self) -> None:
        """Negate every value returned from here on, so callers are given ``f(a) <= 0 <= f(b)``.

        Values already in the history are negated too, so the history shows one
        consistent function: `Solver.solve` decides on normalization only after
        the endpoint evaluations.
        """
        self._is_sign_normalized = True
        if self.history is not None:
            self.history = [(x, -fx) for x, fx in self.history]

    def __call__(self, x: float) -> float:
        """Evaluate ``f`` at ``x``: refuse it past the budget or outside the guard, reject a non-finite value, count it.

        Returns:
            The value as a `CountedFloat`, negated when sign normalization is enabled.
        """
        if self.n_fevals >= self._max_fevals:
            raise MaxFevalsExceeded(f"Evaluation budget of {self._max_fevals} function evaluations exhausted.")
        x_plain = float(x)  # The guards and f itself run on plain floats: uncounted, and numba-compatible.
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
        if self._is_sign_normalized:
            # The sign flip runs on a plain float (fx is wrapped in CountedFloat only at the return below),
            # so it is not counted, even though the f(a) < 0 < f(b) invariant that it establishes can enable
            # solver simplifications (e.g. simpler bracketing conditions).
            #
            # The stance: a user could implement the same flip inside a tested function, where it would
            # go uncounted too, and leaving it uncounted here does not skew comparisons between solvers.
            #
            # Counting the sign flip would compensate those simplifications in only ~half the cases
            # (f(a) > 0) and would make benchmark metrics inconsistent between functions f(.) and -f(.).
            fx = -fx
        if self.history is not None:
            self.history.append((x_plain, fx))
        return CountedFloat(fx)
