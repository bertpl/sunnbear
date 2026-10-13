"""`Bisection` is the reference bracketing solver."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class Bisection(BracketingSolver):
    """`Bisection` splits the interval at its midpoint every iteration, so each iteration halves the width.

    The evaluation count is known in advance: with the interval width ``b - a`` and the tolerance ``xtol``, a
    solve performs ``ceil(log2((b - a) / (2 * xtol)))`` iterations, 1 evaluation each, plus the 2 evaluations at
    the interval bounds.

    The solve performs fewer evaluations when a midpoint is an exact root. Rounding changes the count in 2 cases:

    - near an ``xtol`` at which the formula's count changes by 1, the rounded midpoints can shift the count by 1
      when ``a`` and ``b`` are not exact binary fractions;
    - when ``2 * xtol`` lies close to the float spacing near the root, the count can differ too; when
      ``2 * xtol`` is below that spacing, the midpoint of 2 adjacent floats equals an interval bound, so the
      stopping criterion never holds and the solve ends as ``MAX_FEVALS``.

    The benchmark relies on the evaluation count of `Bisection` as its reference cost, so the count must not change.

    `Bisection` stops by `BracketingSolver`'s criterion, so the returned x-value lies within ``xtol`` of a root.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd
          edition, section 9.1.1. Cambridge University Press. The book's routine ``rtbis`` returns an evaluated
          interval bound, the one where ``f <= 0``, not the midpoint.
        - Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition, section 2.1.
          John Wiley & Sons. The test suite reproduces the book's Table 2.1.
        - SciPy's ``scipy.optimize.bisect``, which adds a relative term to its tolerance; the test suite checks
          `Bisection` against ``scipy.optimize.bisect``.
    """

    name = "bisection"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the midpoint."""
        return interval.midpoint
