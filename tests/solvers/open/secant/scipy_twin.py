"""`SecantScipyTwin` runs SciPy's secant method as a `Solver`, so `Secant` can be tested against it."""

import scipy.optimize

from sunnbear.solvers import Interval
from tests.solvers.twins import StoppingWrappedFunction, TwinConvergedSignal, TwinSolver


class SecantScipyTwin(TwinSolver):
    """`SecantScipyTwin` runs SciPy's secant method, which is `scipy.optimize.newton` called without a derivative. It
    starts from the interval bounds and returns the point where SciPy stops.

    `Secant` stops by SciPy's own rule, so the twin passes SciPy ``tol=xtol`` and ``rtol=0``; SciPy then stops where
    `Secant` stops, and the twin never interrupts SciPy.

    The twin deviates from exact agreement in 1 declared way: SciPy evaluates both interval bounds again before its
    first step.
    """

    name = "secant_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's secant method from ``a`` and ``b``, and signal its root if it converged."""
        # maxiter caps SciPy's own iterations; the evaluation budget of the twin test cases ends a solve long before
        # SciPy reaches that cap.
        root, info = scipy.optimize.newton(f, a, x1=b, tol=xtol, rtol=0.0, maxiter=10_000, full_output=True, disp=False)
        if info.converged:
            raise TwinConvergedSignal(float(root))

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``None``: SciPy stops by the stopping rule of `Secant`, so the twin never interrupts SciPy."""
        return None
