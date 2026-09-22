"""`WrappedFunction` wraps ``f`` for one solve; every evaluation goes through it.

Each call runs the checks documented on the class, in order.

`Solver.solve` builds one per solve and hands it over inside the `SolveState`;
solver implementations never construct one.
"""

import math
from collections.abc import Callable

from counted_float import CountedFloat, PauseFlopCounting

from .exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded


class WrappedFunction:
    """A `WrappedFunction` wraps ``f`` for one solve; each call runs the checks below.

    A call:

    - raises `MaxFevalsExceeded` when the call would exceed ``max_fevals``,
      before evaluating anything;
    - raises `DivergedError` when ``x`` is not finite, before evaluating anything;
    - evaluates ``f`` with flop counting paused, so only the solver's own
      arithmetic is counted;
    - raises `FunctionDomainError` when ``f`` raises or returns a non-finite value;
    - appends ``(x, f(x))`` to the history when history is on, so the history is the caller's ``f`` as
      evaluated, in call order;
    - returns the value as a `CountedFloat`, so the solver's arithmetic on it
      is counted.

    The evaluation count includes calls that ended in `FunctionDomainError`,
    since the function was evaluated; the count excludes calls refused by the
    budget or for a non-finite ``x``.

    Whether an evaluation far from the interval is divergence is not decided here: `Solver.solve`
    judges that from where the solve ended and where a function error happened.
    """

    def __init__(
        self,
        f: Callable[[float], float],
        *,
        max_fevals: int,
        history_enabled: bool,
    ) -> None:
        """Wrap ``f`` for one solve."""
        self._f = f
        self._max_fevals = max_fevals
        self.n_fevals = 0
        self.history: list[tuple[float, float]] | None = [] if history_enabled else None

    def __call__(self, x: float) -> float:
        """Evaluate ``f`` at ``x``: refuse it past the budget or for a non-finite ``x``, reject a failed evaluation."""
        if self.n_fevals >= self._max_fevals:
            raise MaxFevalsExceeded(f"Evaluation budget of {self._max_fevals} function evaluations exhausted.")
        x_plain = float(x)  # The checks and f itself run on plain floats: uncounted, and numba-compatible.
        if not math.isfinite(x_plain):
            raise DivergedError(f"Evaluation requested at x={x_plain!r}, which is not finite.")
        with PauseFlopCounting():
            try:
                fx = float(self._f(x_plain))
            except Exception as exc:  # Whatever f raises is a function error at this x, by design.
                self.n_fevals += 1
                raise FunctionDomainError(x_plain, f"f({x_plain!r}) raised {exc!r}.") from exc
        self.n_fevals += 1
        if not math.isfinite(fx):
            raise FunctionDomainError(x_plain, f"f({x_plain!r}) = {fx!r} is not finite.")
        if self.history is not None:
            self.history.append((x_plain, fx))
        return CountedFloat(fx)
