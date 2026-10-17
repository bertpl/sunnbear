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

    `Bisection` follows the pseudocode ``Bisect`` of Atkinson (1989), with 2 deviations:

    - **Exact zeros:** a function value of 0 at a midpoint ends the solve, as in SciPy, while ``Bisect`` bisects on
      past such a midpoint;
    - **Stopping criterion:** `Bisection` stops by `BracketingSolver`'s criterion, ``b - a <= 2 * xtol`` before the
      next midpoint, while ``Bisect`` tests ``b - c <= epsilon`` after evaluating the midpoint ``c``; in rare cases,
      the evaluation counts of `Bisection` and ``Bisect`` then differ by 1.

    The returned x-value lies within ``xtol`` of a root.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd
          edition, section 9.1.1. Cambridge University Press. The book's routine ``rtbis`` returns an evaluated
          interval bound, the one where ``f <= 0``, not the midpoint.
        - Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition, section 2.1.
          John Wiley & Sons. It provides the pseudocode ``Bisect``, and the test suite reproduces its Table 2.1.
        - SciPy's ``scipy.optimize.bisect``, which adds a relative term to its tolerance; the test suite checks
          `Bisection` against ``scipy.optimize.bisect``.
        - Third parties that publish evaluation counts of bisection:

          - Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear
            function without using derivatives. Advances in Engineering Software 28(3), 145-149. Its Table 2
            holds the column "Bisection". https://doi.org/10.1016/S0965-9978(96)00051-8
          - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
            Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table 2 holds the column "bs".
            https://doi.org/10.3390/a19050332
    """

    name = "bisection"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the midpoint."""
        return interval.midpoint
