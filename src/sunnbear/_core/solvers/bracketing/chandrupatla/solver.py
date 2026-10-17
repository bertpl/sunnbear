"""`Chandrupatla` implements Chandrupatla's method, which interpolates only where interpolation is well conditioned."""

import math

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.stopping import interval_root, is_interval_converged


class Chandrupatla(Solver):
    """`Chandrupatla` implements Chandrupatla's method, following the BASIC listing ``NEWZERO.BAS`` of its paper.

    The method, from Chandrupatla (1997), keeps 3 x-values:

    - ``x1``, the newest x-value;
    - ``x2``, the other interval bound, where ``f`` has the other sign;
    - ``x3``, the bound that the last iteration dropped from the interval.

    ``f1``, ``f2`` and ``f3`` are the values of ``f`` at these x-values. Each iteration evaluates
    ``x = x1 + t*(x2 - x1)``, where ``t`` comes from 1 of 2 rules:

    - inverse quadratic interpolation through the 3 x-values, where the paper shows it to be well conditioned:
      ``1 - sqrt(1 - xi) < phi < sqrt(xi)``, with ``xi = (x1 - x2) / (x3 - x2)`` and
      ``phi = (f1 - f2) / (f3 - f2)``;
    - bisection, ``t = 0.5``, everywhere else, and in the first iteration.

    ``t`` is then kept at least ``tl = tol / |x2 - x1|`` away from 0 and 1, with ``tol`` the tolerance defined below,
    so that every new x-value lies at least ``tol`` inside the interval.

    The paper's tolerance is ``tol = 2*eps_r*|xm| + 0.5*eps_a``, where:

    - ``eps_r`` is a relative tolerance;
    - ``eps_a`` is an absolute tolerance;
    - ``xm`` is the interval bound with the smaller ``|f|``.

    After each evaluation, the solve ends once the interval is at most ``2*xtol`` wide, or once ``f`` is 0 at an
    interval bound. It returns that bound, or else the interval's midpoint, which then lies within ``xtol`` of a root.

    `Chandrupatla` sets ``eps_a = 2*xtol`` and ``eps_r = 0``, so ``tol = xtol``, half the width at which the solve
    ends. While the solve continues, the interval is wider than ``2*tol``, so ``tl < 0.5``, and the limits ``tl`` and
    ``1 - tl`` on ``t`` do not cross.

    The flowchart in the paper's Fig. 1 swaps the yes and no labels of its sign test, relative to the listing
    ``NEWZERO.BAS``; `Chandrupatla` follows the listing.

    `Chandrupatla` deviates from the listing in its stopping criterion and its return value: the listing stops once
    ``tl > 0.5``, that is once the interval is narrower than ``2*tol``, or once ``f(xm)`` is 0, and returns ``xm``,
    which then lies within ``2*tol`` of a root.

    `Chandrupatla` tracks a third x-value besides the 2 interval bounds, so it writes its own loop, not
    `BracketingSolver`'s.

    References:
        - Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear
          function without using derivatives. Advances in Engineering Software 28(3), 145-149. `Chandrupatla`
          follows the paper's BASIC listing ``NEWZERO.BAS``, and the test suite reproduces the paper's Table 2.
          https://doi.org/10.1016/S0965-9978(96)00051-8
        - SciPy's ``scipy.optimize.elementwise.find_root``, which its documentation says uses Chandrupatla's
          algorithm, and which adds a relative tolerance on ``x`` and tolerances on ``f``; the test suite checks
          `Chandrupatla` against ``scipy.optimize.elementwise.find_root``.
    """

    name = "chandrupatla"
    version = 2

    def _solve(self, state: SolveState) -> float:
        """Run the loop of the paper's BASIC listing and return the root estimate of `_root_if_converged`.

        The variables keep the names of the BASIC listing, so that the code can be compared with the listing line by
        line, except where a listing name would read as an interval bound or its ``f`` value in this package, as
        ``A`` and ``B`` would read as the bounds ``a`` and ``b``. Besides the variables of the class docstring, the
        code uses these variables:

        - ``phi``, which the listing calls ``PH``;
        - ``phi_low`` and ``phi_high``, the lower and upper limits on ``phi``, which the listing calls ``FL`` and
          ``FH``;
        - ``al``, which is ``(x3 - x1) / (x2 - x1)``;
        - ``q1``, ``q2``, ``q3`` and ``q4``, the 4 quotients that make up the interpolated ``t``, which the listing
          calls ``A``, ``B``, ``C`` and ``D``.

        Each iteration:

        - evaluates ``x`` and makes it ``x1``;
        - ends the solve once `_root_if_converged` returns a root estimate, where the listing tests its own stopping
          criterion;
        - chooses ``t`` for the next iteration.
        """
        interval = state.interval
        x1, f1, x2, f2 = interval.a, interval.fa, interval.b, interval.fb
        xtol_doubled = 2.0 * state.xtol
        # tol is the listing's tolerance 2*eps_r*|xm| + 0.5*eps_a, with eps_a = 2*xtol and eps_r = 0.
        tol = state.xtol
        t = 0.5
        while True:
            # --- the new x-value x --------------
            x = x1 + t * (x2 - x1)
            f = state.f(x)
            state.x_best = x
            # Reorder the x-values into the class docstring's roles for x1, x2 and x3, as the listing's step
            # "Arrange 2-1-3" does. When f is exactly 0, which branch runs does not matter, because the stopping
            # criterion below then returns x.
            if (f > 0.0) == (f1 > 0.0):
                x3, f3 = x1, f1
            else:
                x3, f3 = x2, f2
                x2, f2 = x1, f1
            x1, f1 = x, f

            # --- the stopping criterion ---------
            x_root = self._root_if_converged(x1, f1, x2, f2, xtol_doubled)
            if x_root is not None:
                return x_root

            # --- t for the next x-value ---------
            xi = (x1 - x2) / (x3 - x2)
            phi = (f1 - f2) / (f3 - f2)
            phi_low = 1.0 - math.sqrt(1.0 - xi)
            phi_high = math.sqrt(xi)
            if phi_low < phi and phi < phi_high:
                al = (x3 - x1) / (x2 - x1)
                q1 = f1 / (f2 - f1)
                q2 = f3 / (f2 - f3)
                q3 = f1 / (f3 - f1)
                q4 = f2 / (f3 - f2)
                t = q1 * q2 + q3 * q4 * al
            else:
                t = 0.5
            tl = tol / abs(x2 - x1)
            if t < tl:
                t = tl
            if t > 1.0 - tl:
                t = 1.0 - tl

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _root_if_converged(x1: float, f1: float, x2: float, f2: float, xtol_doubled: float) -> float | None:
        """Return the root estimate if the solve ends at these interval bounds, or ``None`` if it continues.

        The solve ends by the shared stopping criterion, `is_interval_converged`, and returns `interval_root`. The
        test suite overrides this method to apply the listing's own stopping criterion where it reproduces the
        paper's published counts.
        """
        if is_interval_converged(x1, f1, x2, f2, xtol_doubled):
            return interval_root(x1, f1, x2, f2)
        else:
            return None
