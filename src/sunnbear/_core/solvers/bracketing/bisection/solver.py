"""`Bisection` is the reference bracketing solver.

The rest of this docstring is the record of `Bisection` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - none: bisection is a classical method with no article of its own.
    - II - authors' code:
      - none.
    - III - third party:
      - Atkinson (1989), section 2.1: the pseudocode ``Bisect``, and Table 2.1, its results on 1 problem;
      - Press et al. (2007), section 9.1.1: prose and the routine ``rtbis``;
      - SciPy's ``scipy.optimize.bisect``.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows Atkinson's ``Bisect``, except:
    - Exact zeros follow SciPy, which P1 prefers: a function value of 0 at a bound or a midpoint ends the solve.
      Atkinson excludes a zero bound, and bisects on past a zero midpoint.
    - JUDGMENT-CALL: the stopping test is ``b - a <= 2 * xtol`` before the midpoint (`Interval.is_converged`), not
      Atkinson's ``b - c <= epsilon`` after it, so that `Bisection` keeps the loop of `BracketingSolver`. The
      evaluation count differs by 1 in about 1 in 100,000 solves; accuracy is the same.
    - JUDGMENT-CALL: Atkinson's stopping rule, not SciPy's, which P1 prefers. SciPy also evaluates the midpoint that
      it returns: 1 evaluation more, for the same result.
    - JUDGMENT-CALL: Atkinson's midpoint, not SciPy's ``a + dm`` (``dm`` the half-width, halved each iteration),
      which P1 prefers. The evaluation count differs by 1 in about 1 in 7,000 solves; accuracy is the same.
    - Translation of ``xtol`` (P7): ``xtol`` is Atkinson's ``epsilon``.

Validation:
    - A - authors' results:
      - none exists.
    - B - third-party results:
      - used: Atkinson's Table 2.1, reproduced exactly, which is convincing (P5);
      - TBD: Chandrupatla (1997), Table 2, the column "Bisection", which no test checks yet: `Bisection` with
        ``xtol = 0.5e-5`` reproduces all 45 counts;
      - TBD: Ganchovski et al. (2026), Table 2, the column "bs": not compared yet.
    - C - reference implementation:
      - used: a twin test checks the midpoints against SciPy's ``scipy.optimize.bisect``, not its stopping rule.

Variants:
    - `BisectionConfig`, the only config, is the baseline, which follows the principles as strictly as a core variant
      (P8).
"""

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
