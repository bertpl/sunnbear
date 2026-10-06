"""`Ridders` implements Ridders' method: each iteration evaluates the midpoint, then a point from an exponential fit."""

import math
from typing import Literal

from sunnbear._core.solvers.core import Solver, SolveState


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
    ``variant`` therefore picks 1 of 3 variants, each from a reference implementation:

    - ``"commons_math"``, the stopping criterion of Apache Commons Math's ``RiddersSolver``, close to that of
      Numerical Recipes' ``zriddr``: the solve stops once 2 successive iterates lie at most ``xtol`` apart, and
      returns the last one. On a function that is not smooth, that iterate often lies more than ``xtol`` from the
      true root.
    - ``"scipy"``, SciPy's ``ridder``: the step from ``x1`` is limited to ``d - xtol / 2``, so that ``x3`` lies at
      least ``xtol / 2`` inside the interval. The solve stops once the interval is narrower than ``xtol``, and
      returns the last iterate. SciPy adds a relative term to its tolerance; this variant leaves it out, so that its
      root always lies within ``xtol`` of the true root.
    - ``"bracketing_solver"``, the stopping criterion of `BracketingSolver`: the solve stops once the interval is at
      most ``2 * xtol`` wide, and returns its midpoint, which always lies within ``xtol`` of the true root.

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
          Transactions on Circuits and Systems 26(11), 979-980. https://doi.org/10.1109/TCS.1979.1084580
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section
          9.2.1. Cambridge University Press. The book's routine ``zriddr`` is close to the ``"commons_math"``
          variant.
        - SciPy's ``scipy.optimize.ridder``, which the ``"scipy"`` variant follows; the test suite checks `Ridders`
          against ``scipy.optimize.ridder``.
        - Apache Commons Math's ``org.apache.commons.math4.legacy.analysis.solvers.RiddersSolver``, whose stopping
          criterion the ``"commons_math"`` variant follows.
    """

    name = "ridders"
    version = 1

    def __init__(self, *, variant: Literal["commons_math", "scipy", "bracketing_solver"]) -> None:
        """Configure the variant; the class docstring describes each.

        Raises:
            ValueError: If ``variant`` is not 1 of the values in its annotation.
        """
        if variant not in ("commons_math", "scipy", "bracketing_solver"):
            raise ValueError(f"variant must be 'commons_math', 'scipy' or 'bracketing_solver' (got {variant!r}).")
        self.variant = variant

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — one loop holds the criteria of all 3 variants
        """Run Ridders' iterations and return the root estimate.

        Each iteration evaluates the midpoint ``x1`` and then the iterate ``x3``, and splits the interval at both. The
        solve ends at an evaluation that returns exactly 0, or once the stopping criterion of the variant holds.
        """
        interval = state.interval
        if self.variant == "scipy":
            xtol_halved = 0.5 * state.xtol
        elif self.variant == "bracketing_solver":
            xtol_doubled = 2.0 * state.xtol
        x3_previous: float | None = None  # The commons_math variant compares each new x3 with this previous one.
        while True:
            # --- bracketing_solver criterion ----
            # It is checked before each iteration, so that an interval that is narrow enough costs no evaluation.
            if self.variant == "bracketing_solver" and interval.width <= xtol_doubled:
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
            if self.variant == "scipy":
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
            if self.variant == "commons_math":
                if x3_previous is not None and abs(x3 - x3_previous) <= state.xtol:
                    return x3
                x3_previous = x3
            elif self.variant == "scipy" and interval.width < state.xtol:
                return x3
