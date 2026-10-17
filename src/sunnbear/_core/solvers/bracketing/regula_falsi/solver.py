"""`RegulaFalsi` implements regula falsi, the bracketing algorithm based on linear interpolation."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState
from sunnbear._core.solvers.core.formulas import chord_zero


class RegulaFalsi(BracketingSolver):
    """`RegulaFalsi` evaluates, every iteration, the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``.

    `RegulaFalsi` implements the classic method, without any of the modifications that repair its
    known weakness: when the function is convex or concave on the interval, 1 interval bound is
    retained forever and the width never shrinks below the distance from that bound to the root, so
    the stopping criterion never holds.

    The other bound is replaced every iteration and keeps approaching the root. Such a solve runs
    until its evaluation budget is exhausted and ends as ``MAX_FEVALS``. Its ``result.x`` is then the
    last evaluated x-value, which is close to the root.

    `RegulaFalsi` deviates from its sources in 1 place:

    - **Stopping criterion:** `RegulaFalsi` stops by `BracketingSolver`'s criterion, so the returned x-value lies
      within ``xtol`` of a root, unless the solve stalls; the routine ``rtflsp`` of Press et al. (2007) stops once an
      evaluation moves an interval bound by less than its tolerance, and does not test the width of the interval.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press. It describes the method, which it calls false position.
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. Its equation 3 is the iteration formula, in the form that `chord_zero` computes.
    """

    name = "regula_falsi"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``."""
        return chord_zero(interval.a, interval.fa, interval.b, interval.fb)
