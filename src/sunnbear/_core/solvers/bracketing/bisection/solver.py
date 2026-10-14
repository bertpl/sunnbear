"""`Bisection` is the reference bracketing solver.

The rest of this docstring is the record of `Bisection` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package): which source each aspect of the solver
follows, and how the solver is validated.

Sources:
    - article:

      - none: bisection is a classical method with no article of its own, so its sources start at third party (P1).
    - authors' code:

      - none.
    - third party:

      - Atkinson (1989), section 2.1: the pseudocode ``Bisect``, which states every aspect below, and Table 2.1, its
        results on 1 problem;
      - Press et al. (2007), section 9.1.1: prose and the routine ``rtbis``;
      - SciPy's ``scipy.optimize.bisect``.
    - own judgment:

      - none.

Source per aspect:
    No article or authors' code exists, so every aspect follows a third party: Atkinson's ``Bisect``, except where an
    entry names another source.

    - Step formula: Atkinson's steps 1 and 3. Each iteration evaluates the midpoint ``c`` and keeps the half of the
      interval whose bounds' function values differ in sign; a ``c`` with ``f(c) = 0`` replaces ``a``. Press et al.
      and SciPy state the same step.
    - Safeguards: none, as in Atkinson. Atkinson notes that ``Bisect`` ignores the limits of machine precision, and
      that a practical program would adjust its tolerance to them, without giving a rule.

      The benchmark keeps ``xtol`` well above the float spacing at the interval bounds (`compute_xtol_range`), so a
      solve in the benchmark never ends with the status ``MAX_FEVALS``, the end of the evaluation budget, because a
      midpoint equals an interval bound. Press et al. and SciPy cap the number of iterations; in sunnbear, the
      evaluation budget caps it for every solver.
    - Constants: Atkinson's factor ``1/2`` in the midpoint, and Atkinson's tolerance ``epsilon`` as the bound on the
      half-width ``b - c``.
    - Stopping rule: Atkinson's step 2, which ends the solve once the half-width ``b - c`` is at most ``epsilon`` and
      returns ``c`` without evaluating it. `BracketingSolver` implements it in a form that is equal in exact
      arithmetic but rounds differently in float64, through `Interval.is_converged` and `Interval.root` (see the
      JUDGMENT-CALL on the stopping test below).

      When a function value is exactly 0, where Atkinson states nothing or differs from SciPy, the solver follows
      SciPy, the source that P1 favors when 2 sources of the same rank differ:

      - a zero at a bound of the initial interval ends the solve before the first midpoint; Atkinson requires
        ``f(a) * f(b) < 0``;
      - a midpoint with ``f(c) = 0`` ends the solve and is returned; Atkinson's step 3 makes it the bound ``a`` and
        bisects on. Table 2.1 has no such midpoint, so Atkinson's handling and SciPy's both reproduce it.
    - JUDGMENT-CALL: the stopping test is ``b - a <= 2 * xtol``, computed before ``c`` (`Interval.is_converged`), not
      Atkinson's ``b - c <= epsilon``, computed after it, so that `Bisection` keeps the solve loop that it inherits
      from `BracketingSolver`. The 2 tests are equal in exact arithmetic and cost the same flops. In float64 they give
      a different evaluation count in about 1 in 100,000 solves with ``xtol`` inside the benchmark's range, and the
      choice does not change the accuracy of the returned x-value.
    - JUDGMENT-CALL: the solver keeps Atkinson's stopping rule, not SciPy's, which P1 favors as the most widely used
      implementation. SciPy evaluates each midpoint first, then ends the solve once the halved interval is narrower
      than ``xtol + rtol * |c|``, and returns that midpoint. It returns the x-value that Atkinson's rule returns, after
      1 evaluation more, so the choice saves that evaluation and changes no result.
    - Arithmetic form (P6): P6 allows both changes of form:

      - Atkinson's ``(a + b) / 2`` is computed as ``0.5 * (a + b)``;
      - Atkinson's sign test ``sign(f(b)) * sign(f(c)) <= 0`` is computed as a comparison of ``f(c)`` with 0, in the
        direction that depends on whether ``f`` is negative or positive at ``a``.
    - JUDGMENT-CALL: the solver keeps Atkinson's form of the midpoint, which `Interval.midpoint` gives every
      bracketing solver, not SciPy's, which P1 favors as the most widely used implementation. SciPy computes the
      midpoint as ``a + dm``, with the half-width ``dm`` halved each iteration, at the same flop count. Its midpoints
      can differ from ``0.5 * (a + b)`` in the last bit, which changes the evaluation count in about 1 in 7,000 solves
      with ``xtol`` inside the benchmark's range, and does not change the accuracy of the returned x-value.
    - Translation of ``xtol`` (P7): none needed. Atkinson's ``epsilon`` bounds the distance from ``c`` to a root, as
      ``xtol`` does, so ``xtol`` is passed as ``epsilon``.

Validation:
    - A, the authors' own published results: none exists, because bisection has no article of its own.
    - B, a third party's published results: used. The test suite reproduces Atkinson's Table 2.1 exactly, so the
      reproduction is convincing (P5). Chandrupatla (1997) and Ganchovski et al. (2026) publish evaluation counts of
      bisection too, which the test suite does not check.
    - C, parity with a reference implementation: used. The test suite checks that `Bisection` evaluates the same
      x-values as SciPy's ``scipy.optimize.bisect``, on every twin test case. The twin test runs
      ``scipy.optimize.bisect`` with the stopping rule of `Bisection`, so C checks the step and its arithmetic, not
      the stopping rule.

Variants:
    - `BisectionConfig`, the only config, has role ``BUILTIN_BASELINE``: the benchmark uses its evaluation count as
      its reference cost. As the baseline, it follows the principles as strictly as a core variant (P8).
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
