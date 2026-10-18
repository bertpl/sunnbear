"""`Ridders` implements Ridders' method: each iteration evaluates the midpoint, then the zero of an exponential fit."""

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

    The paper states no stopping criterion, only that the procedure can end once a given accuracy is reached.
    ``variant``, a value of `RiddersVariant`, picks 1 of 3 stopping criteria. Every variant checks for a 0 right after
    evaluating ``x1``, and checks its whole criterion after evaluating ``x3``, as SciPy's ``ridder`` does:

    - ``"standard_stopping_criterion"``, the shared stopping criterion of the bracketing solvers: the solve ends once
      the interval is at most ``2*xtol`` wide, or once the function value at an interval bound is exactly 0. It
      returns that bound, or else the interval's midpoint, which then lies within ``xtol`` of a root. The split at
      ``x1`` makes ``x1`` an interval bound, so a 0 at ``x1`` meets this criterion.
    - ``"scipy"``, the stopping criterion of SciPy's ``ridder``: the solve ends at an evaluation that returns exactly
      0, or once the interval is narrower than ``xtol``, and returns the last evaluated x-value.
    - ``"commons_math"``, the stopping criterion of Apache Commons Math's ``RiddersSolver``: the solve ends at an
      evaluation that returns exactly 0, or once 2 successive iterates ``x3`` lie at most ``xtol`` apart, and returns
      the last evaluated x-value. That x-value can lie more than ``xtol`` from a root, as on a function with a kink or
      with a multiple root.

    `Ridders` departs from its sources, or settles a detail that they leave open, in these places:

    - **Limit on the step:** only ``"scipy"`` limits the step from ``x1``, as SciPy does, so that ``x3`` lies at least
      ``xtol/2`` inside the interval; the paper and Commons Math state no limit.

      Near the root, the limit shrinks the interval to the stopping width in fewer evaluations: without it, ``x3`` can
      land between the root and the interval bound on the root's side of ``x1``, and the interval then only halves, so
      the evaluation counts of ``"standard_stopping_criterion"`` vary more between near-identical functions;
    - **SciPy's tolerance:** ``"scipy"`` leaves out the relative term that SciPy adds to ``xtol``, so that its returned
      x-value always lies within ``xtol`` of a root, and leaves out SciPy's iteration limit ``maxiter``, so that only
      the evaluation budget ends a long solve;
    - **Commons Math's tolerances:** ``"commons_math"`` sets Commons Math's relative accuracy and function value
      accuracy to 0, so that ``xtol``, its absolute accuracy, is its only tolerance;
    - **Order of the step's operations:** `Ridders` computes ``(d * (f1 / f0)) / sqrt(...)``, as SciPy does, where
      equation 6 multiplies ``d`` by the quotient ``(f1 / f0) / sqrt(...)``; the 2 orders are equal in exact arithmetic
      but round differently;
    - **Midpoint:** `Ridders` computes it as ``0.5*(a + b)``, with `Interval.midpoint`; SciPy computes it as
      ``xa + 0.5*(xb - xa)``.

    An iteration evaluates the function twice, so `Ridders` writes its own loop, not `BracketingSolver`'s.

    References:
        - Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous function. IEEE
          Transactions on Circuits and Systems 26(11), 979-980. Its equation 6 is the step, and the test suite
          reproduces the first iteration of its example and the iterates of its Section III.
          https://doi.org/10.1109/TCS.1979.1084580
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section
          9.2.1. Cambridge University Press. It describes the method, as the routine ``zriddr``.
        - SciPy's ``scipy.optimize.ridder``, which gives the stopping criterion and the limit on the step of
          ``"scipy"``, and the points at which ``"standard_stopping_criterion"`` checks its stopping criterion; the test
          suite checks `Ridders` against ``scipy.optimize.ridder``.
        - Apache Commons Math's ``org.apache.commons.math4.legacy.analysis.solvers.RiddersSolver``, which gives the
          stopping criterion of ``"commons_math"``. https://github.com/apache/commons-math
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table 2 holds the column "Rid",
          from C# code that stops as ``"commons_math"`` does, and the test suite reproduces that column with
          ``"commons_math"`` and ``"scipy"``. https://doi.org/10.3390/a19050332
    """

    name = "ridders"
    version = 2

    def __init__(self, *, variant: RiddersVariant) -> None:
        """Configure the variant; the class docstring describes each. A plain string such as ``"scipy"`` works too.

        Raises:
            ValueError: If ``variant`` is not a value of `RiddersVariant`.
        """
        self.variant = RiddersVariant(variant)

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — one loop holds the stopping criteria of all 3 variants
        """Run Ridders' iterations and return the root estimate.

        Each iteration evaluates the midpoint ``x1`` and then the iterate ``x3``, and splits the interval at both. A 0
        at ``x1`` ends the solve right after its evaluation, and the variant's whole stopping criterion is checked after
        evaluating ``x3``; there is no check before the first iteration.
        """
        interval = state.interval
        if self.variant is RiddersVariant.SCIPY:
            xtol_halved = 0.5 * state.xtol
        elif self.variant is RiddersVariant.STANDARD_STOPPING_CRITERION:
            xtol_doubled = 2.0 * state.xtol
        x3_previous: float | None = None  # The commons_math variant compares each new x3 with this previous one.
        while True:
            # --- x1, the midpoint ---------------
            x1 = interval.midpoint
            f1 = state.f(x1)
            state.x_best = x1
            # For standard_stopping_criterion, a 0 at x1 meets the shared criterion: the split at x1 makes x1 an
            # interval bound, which the shared criterion returns.
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
            # The scipy and commons_math variants return x3 at a 0, as their reference implementations do.
            if self.variant is not RiddersVariant.STANDARD_STOPPING_CRITERION and f3 == 0.0:
                return x3
            interval = interval.split_at(x1, f1).split_at(x3, f3)

            # --- criteria after an iteration ----
            if self.variant is RiddersVariant.STANDARD_STOPPING_CRITERION:
                # A 0 at x3 makes x3 an interval bound, so the shared criterion holds there and returns x3.
                if interval.is_converged(xtol_doubled):
                    return interval.root()
            elif self.variant is RiddersVariant.COMMONS_MATH:
                if x3_previous is not None and abs(x3 - x3_previous) <= state.xtol:
                    return x3
                x3_previous = x3
            elif self.variant is RiddersVariant.SCIPY and interval.width < state.xtol:
                return x3
