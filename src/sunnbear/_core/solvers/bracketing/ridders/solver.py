"""`Ridders` implements Ridders' method: each iteration evaluates the midpoint, then the zero of an exponential fit.

The rest of this docstring is the record of `Ridders` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package). ``Source per aspect:`` describes the core
variant, ``"scipy"``, and ``Variants:`` gives the deviations of the other 2 variants.

Sources:
    - I - article:
      - Ia - article code: none;
      - Ib - article pseudocode: none;
      - Ic - article text: Ridders (1979), section I: its equation 6, and the interval update, which the article's
        example in Fig. 2 applies by keeping the narrower of 2 intervals that hold the sign change. The article states
        no stopping rule, only that the procedure can end once a given accuracy is obtained.
    - II - authors' code:
      - none.
    - III - third party:
      - SciPy's ``scipy.optimize.ridder``: a stopping rule on the interval width, and a limit on the step that keeps
        ``x3`` inside the interval;
      - Apache Commons Math's ``RiddersSolver``: a stopping rule on the distance between 2 successive iterates;
      - Press et al. (2007), section 9.2.1: the routine ``zriddr``, which stops on that distance or on the interval
        width;
      - Ganchovski et al. (2026): the C# code behind its Table 2, which stops as Commons Math does;
      - Oliveira and Takahashi (2020), section 3.1: runs of the method that stop by the rule of `BracketingSolver`.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows Ridders (1979), except:
    - Exact zeros and the stopping rule follow SciPy, which P1 prefers among the third-party sources, since the
      article states neither: a function value of 0 ends the solve at its x-value; otherwise the solve ends once the
      interval is narrower than ``xtol``, and returns ``x3``, which then lies within ``xtol`` of a root.
    - JUDGMENT-CALL: SciPy's iteration limit ``maxiter`` is left out, so the evaluation budget ends a long solve, as
      for every solver. Where SciPy raises an error after ``maxiter`` iterations, the solve runs on to its budget.
    - PRINCIPLE-GAP (P1): SciPy limits the step, so that ``x3`` lies at least ``xtol / 2`` inside the interval;
      equation 6 has no limit, and P1 does not say whether an article that mentions no safeguard leaves the
      safeguards to the next-ranked source. The code keeps SciPy's limit; without it, the interval often only halves
      near the root, and the solve takes 68 evaluations against 12 on ``x^3 - x - 0.801`` over ``[1, 2]`` at
      ``xtol = 1e-10``.
    - PRINCIPLE-CONFLICT (P1): on an initial interval narrower than ``xtol``, the limit ``d - xtol / 2`` is negative;
      the code then moves ``x3`` from the midpoint in the step's direction, and SciPy against it. On an interval
      narrower than ``xtol / 2``, either form puts ``x3`` outside the interval, and the solve ends as ``DIVERGED``.
      Computing the limit as SciPy does would resolve the conflict; the benchmark never meets the case, because it
      picks every ``xtol`` below the width of the initial interval.
    - JUDGMENT-CALL: the midpoint is ``0.5 * (a + b)``, the framework's `Interval.midpoint`, as Commons Math,
      Press et al. and the C# code compute it; SciPy, which P1 prefers where the article gives no formula, computes
      ``a + 0.5 * (b - a)``. SciPy's form changes the evaluated x-values in their last bits in about 1 in 8 solves,
      and the evaluation count in about 1 in 100.
    - PRINCIPLE-CONFLICT (P6): the code computes the step as ``d * r / sqrt(r * r - f2 / f0)``, with ``r = f1 / f0``,
      so it multiplies ``d * r`` first, as SciPy does; equation 6 multiplies ``d`` by the fraction
      ``r / sqrt(r^2 - f2 / f0)``. Computing equation 6 as printed would resolve the conflict: it changes the evaluated
      x-values in their last bits in about 1 in 3 solves, and the evaluation count in about 1 in 100; all 30 iterates
      of Section III still match, and 74 of the 92 counts of Table 2 of Ganchovski et al. (2026) match with either form.
    - Translation of ``xtol`` (P7): ``xtol`` is SciPy's ``xtol``, with SciPy's relative tolerance ``rtol`` at 0, a
      value that SciPy itself does not accept; ``xtol`` thus sets both the width at which the solve stops and the
      limit on the step.

Validation:
    - A - authors' results:
      - used: the first iteration of the example in section I, and all 30 iterates that Section III prints for 5 runs,
        which every variant reproduces to the printed digits; this is convincing (P5);
      - not used: the number of iterates in each run of Section III, because the article states no stopping rule.
    - B - third-party results:
      - used: Ganchovski et al. (2026), Table 2, the column "Rid", reproduced convincingly (P5): 74 of the 92
        evaluation counts exactly, and the test data states the cause of each other count. The C# code's stopping
        rule, which the variant ``"commons_math"`` shares, causes 11 of them; that variant matches 85 counts.
      - not used: the Ridders results of 2 other articles; the docstring of the test package
        ``tests.solvers.bracketing.ridders`` gives the reasons.
      - TBD: Oliveira and Takahashi (2020), Table 1, the column "Ridders'", whose runs stop by `BracketingSolver`'s
        rule, as the variant ``"bracketing_solver"`` does: that variant matches 19 of the 24 counts exactly and 23
        within 2, and 21 and 24 with equation 6 as printed (see the PRINCIPLE-CONFLICT (P6) entry).
    - C - reference implementation:
      - used: a twin test checks that every variant evaluates the same x-values as SciPy's ``scipy.optimize.ridder``;
        the twin test imposes each variant's stopping rule on SciPy, which for the core variant is SciPy's own rule
        without its relative term.

Variants:
    - `RiddersScipyConfig`, the variant ``"scipy"``, is core (P8): its stopping rule is SciPy's, which P1 prefers.
    - `RiddersCommonsMathConfig`, the variant ``"commons_math"``, is secondary (P8). It deviates from P1 in its
      stopping rule, that of Apache Commons Math's ``RiddersSolver``, with ``xtol`` as Commons Math's absolute
      accuracy and its relative and function value accuracies at 0 (P7); like the article, it does not limit the step.
    - `RiddersBracketingSolverConfig`, the variant ``"bracketing_solver"``, is secondary (P8). It deviates from P1 in
      its stopping rule, that of `BracketingSolver` and of the runs of Oliveira and Takahashi (2020); like the
      article, it does not limit the step.
"""

import math

from sunnbear._core.solvers.core import Solver, SolveState

from .variant import RiddersVariant


class Ridders(Solver):
    """`Ridders` implements Ridders' method (Ridders, 1979), in 3 variants.

    Each iteration evaluates the function twice, on the interval ``[x0, x2]``, with ``fi = f(xi)``:

    - at its midpoint ``x1``;
    - at the iterate ``x3 = x1 + d * (f1 / f0) / sqrt((f1 / f0)^2 - f2 / f0)``, with ``d = x1 - x0``. Each value
      ``fi`` is scaled by ``exp(m * xi)``, with ``m`` chosen so that the 3 scaled values lie on a straight line, and
      ``x3`` is where that line crosses 0. The formula for ``x3`` is the paper's final form of the step, its
      equation 6.

    ``x3`` always lies in the half of the interval that holds the sign change, so the next interval is the current
    interval, split first at ``x1`` and then at ``x3``.

    The paper gives no formula for when to stop, only that the procedure can end once a given accuracy is reached.
    ``variant`` therefore picks 1 of the 3 values of `RiddersVariant`, which differ in their stopping criterion; 2 of
    them follow a reference implementation, and 1 follows `BracketingSolver`:

    - ``"commons_math"``, the stopping criterion of Apache Commons Math's ``RiddersSolver``: the solve stops once
      2 successive iterates lie at most ``xtol`` apart, and returns the last one. That iterate can lie more than
      ``xtol`` from a root, as on a function with a kink or with a multiple root.
    - ``"scipy"``, SciPy's ``ridder``: the step from ``x1`` is limited to ``d - xtol / 2``, so that ``x3`` lies at
      least ``xtol / 2`` inside the interval. The solve stops once the interval is narrower than ``xtol``, and
      returns the last iterate. SciPy adds a relative term to its tolerance; this variant leaves it out, so that its
      returned x-value always lies within ``xtol`` of a root.
    - ``"bracketing_solver"``, the stopping criterion of `BracketingSolver`: the solve stops once the interval is at
      most ``2 * xtol`` wide, and returns its midpoint, which always lies within ``xtol`` of a root.

    SciPy's limit on the step makes the evaluation count of ``"scipy"`` vary far less between near-identical functions
    than that of ``"bracketing_solver"``. Near the root, the root lies in the half between ``x1`` and 1 bound, and
    ``x3`` lies close to the root:

    - without the limit, ``x3`` can lie between the root and that bound; the next interval then runs from ``x1`` to
      ``x3``, so it only halves;
    - with the limit, a root within ``xtol / 2`` of that bound makes ``x3`` lie between ``x1`` and the root; the next
      interval then runs from ``x3`` to that bound, so it is narrower than ``xtol``.

    Under every variant, the solve stops as soon as an evaluation returns exactly 0, and returns that x-value.

    An iteration evaluates the function twice, so `Ridders` writes its own loop, not `BracketingSolver`'s.

    References:
        - Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous function. IEEE
          Transactions on Circuits and Systems 26(11), 979-980. The test suite reproduces the first iteration of the
          paper's example, and the iterates of its Section III. https://doi.org/10.1109/TCS.1979.1084580
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section
          9.2.1. Cambridge University Press. The book's routine ``zriddr`` also stops once 2 successive iterates
          lie within its tolerance, with 2 differences:

          - it compares the newest iterate with the previous one before evaluating the newest, and returns the
            previous one;
          - it also stops once the interval is at most its tolerance wide.
        - SciPy's ``scipy.optimize.ridder``, which the ``"scipy"`` variant follows; the test suite checks `Ridders`
          against ``scipy.optimize.ridder``.
        - Apache Commons Math's ``org.apache.commons.math4.legacy.analysis.solvers.RiddersSolver``,
          https://github.com/apache/commons-math, whose stopping criterion the ``"commons_math"`` variant follows,
          with Commons Math's relative accuracy and function value accuracy at 0.
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table 2 holds the column "Rid",
          from the C# code of the paper's supplementary material, which stops as the ``"commons_math"`` variant does
          and which the authors' repository, https://github.com/Just-A-Random-Geek/ModAB-Root-Finding, holds; the
          test suite reproduces that column. https://doi.org/10.3390/a19050332
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
          Table 1 holds the column "Ridders'", for runs that stop by the rule of `BracketingSolver`.
          https://doi.org/10.1145/3423597
    """

    name = "ridders"
    version = 1

    def __init__(self, *, variant: RiddersVariant) -> None:
        """Configure the variant; the class docstring describes each. A plain string such as ``"scipy"`` works too.

        Raises:
            ValueError: If ``variant`` is not a value of `RiddersVariant`.
        """
        self.variant = RiddersVariant(variant)

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — one loop holds the criteria of all 3 variants
        """Run Ridders' iterations and return the root estimate.

        Each iteration evaluates the midpoint ``x1`` and then the iterate ``x3``, and splits the interval at both. The
        solve ends at an evaluation that returns exactly 0, or once the stopping criterion of the variant holds.
        """
        interval = state.interval
        if self.variant is RiddersVariant.SCIPY:
            xtol_halved = 0.5 * state.xtol
        elif self.variant is RiddersVariant.BRACKETING_SOLVER:
            xtol_doubled = 2.0 * state.xtol
        x3_previous: float | None = None  # The commons_math variant compares each new x3 with this previous one.
        while True:
            # --- bracketing_solver criterion ----
            # It is checked before each iteration, so that an interval that is narrow enough costs no evaluation.
            if self.variant is RiddersVariant.BRACKETING_SOLVER and interval.width <= xtol_doubled:
                return interval.midpoint

            # --- x1, the midpoint ---------------
            x1 = interval.midpoint
            f1 = state.f(x1)
            state.x_best = x1
            if f1 == 0.0:
                return x1

            # --- x3, the paper's equation 6 -----
            f1_over_f0 = f1 / interval.fa
            d = x1 - interval.a
            step = d * f1_over_f0 / math.sqrt(f1_over_f0 * f1_over_f0 - interval.fb / interval.fa)
            if self.variant is RiddersVariant.SCIPY:
                # SciPy keeps x3 at least xtol / 2 inside the interval; the class docstring says why that matters.
                step = math.copysign(min(abs(step), d - xtol_halved), step)
            x3 = x1 + step
            f3 = state.f(x3)
            state.x_best = x3
            if f3 == 0.0:
                return x3
            interval = interval.split_at(x1, f1).split_at(x3, f3)

            # --- criteria after an iteration ----
            # The commons_math criterion compares 2 successive iterates, so it is checked after each iteration; SciPy
            # checks its own criterion there too.
            if self.variant is RiddersVariant.COMMONS_MATH:
                if x3_previous is not None and abs(x3 - x3_previous) <= state.xtol:
                    return x3
                x3_previous = x3
            elif self.variant is RiddersVariant.SCIPY and interval.width < state.xtol:
                return x3
