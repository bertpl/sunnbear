"""`RiddersScipyTwin` runs `scipy.optimize.ridder` as a `Solver`, so `Ridders` can be tested against it."""

from typing import Literal

import numpy as np
import scipy.optimize

from sunnbear.solvers import Interval
from tests.solvers.twins import TwinFunction, TwinSolver


class RiddersScipyTwin(TwinSolver):
    """`RiddersScipyTwin` hands the interval to `scipy.optimize.ridder` and returns the root estimate at the point
    where `Ridders`, in the same variant, would stop.

    SciPy stops once its interval is narrower than its tolerance ``xtol + rtol * x``, where ``x`` is SciPy's current
    iterate, and limits each step so that the iterate lies at least half that tolerance inside the interval. The twin
    passes SciPy:

    - for the ``"scipy"`` variant, ``rtol = 4 * eps``, SciPy's smallest accepted value, and an ``xtol`` reduced by
      ``4 * eps * max(|a|, |b|)``, so that SciPy's tolerance never exceeds `Ridders`' ``xtol`` and SciPy does not
      stop first;
    - for the other 2 variants, SciPy's smallest accepted tolerance, so that SciPy's limit on the step moves an
      iterate by a few ulps at most.

    The twin stops SciPy with the criterion of `Ridders` through `_root_if_sunnbear_solver_stops`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first midpoint;
    - SciPy's midpoints and iterates can differ from those of `Ridders` in their last bits, for 4 reasons:

      - SciPy computes each midpoint as a bound plus a halved step;
      - SciPy does not keep its 2 bounds in order, so the bound that serves as ``x0`` in its formula for the iterate
        can differ from the one that `Ridders` uses;
      - before SciPy 1.18, SciPy computed the iterate with an equivalent formula of its own;
      - SciPy limits each step with its own tolerance; in the ``"scipy"`` variant, that limit differs from that of
        `Ridders` by a few ulps, and in the other 2 variants, which have no such limit, it moves an iterate by a few
        ulps at most.
    """

    name = "ridders_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def __init__(self, *, variant: Literal["commons_math", "scipy", "bracketing_solver"]) -> None:
        """Take the variant of the twin's `Ridders` config."""
        self.variant = variant

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's ridder with the variant's tolerances, as the class docstring gives them."""
        eps = float(np.finfo(float).eps)
        if self.variant == "scipy":
            scipy_xtol = xtol - 4.0 * eps * max(abs(a), abs(b))
        else:
            scipy_xtol = float(np.finfo(float).smallest_normal)
        scipy.optimize.ridder(f, a, b, xtol=scipy_xtol, rtol=4.0 * eps)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return the root estimate if `Ridders` stops after the last of ``evaluations``, or ``None`` if it continues.

        `Ridders` stops at a zero, or after an iteration that meets the criterion of its variant. The evaluations
        alternate between a midpoint and an iterate, so an odd count ends with a midpoint, after which `Ridders` stops
        only at a zero.
        """
        x, fx = evaluations[-1]
        if fx == 0.0:
            return x
        elif len(evaluations) % 2 == 1:
            return None
        elif self.variant == "commons_math":
            # The previous iterate lies 2 evaluations back, before the midpoint of this iteration.
            if len(evaluations) >= 4 and abs(x - evaluations[-3][0]) <= xtol:
                return x
            else:
                return None
        elif self.variant == "scipy":
            if interval.width < xtol:
                return x
            else:
                return None
        else:
            return super()._root_if_sunnbear_solver_stops(interval, evaluations, xtol)
