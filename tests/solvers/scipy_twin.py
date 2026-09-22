"""`ScipySolver` wraps a `scipy.optimize` root finder as a `Solver`, so a shipped solver can be checked against it.

A twin exists for agreement tests only: it is never registered, never benchmarked, and SciPy runs on
plain floats, so the twin's flop counts hold only the framework's own checks. SciPy evaluates ``f`` at the
interval bounds itself, so a twin's ``n_fevals`` is 2 more than SciPy's own function-call count.
"""

from collections.abc import Callable

from sunnbear.solvers import Solver, SolveState

ScipyRootFinder = Callable[..., tuple[float, object]]  # e.g. scipy.optimize.bisect with full_output=True


class ScipySolver(Solver):
    """`ScipySolver` runs 1 `scipy.optimize` root finder on the interval and returns its root."""

    name = "scipy_solver"
    version = 1

    def __init__(self, root_finder: ScipyRootFinder) -> None:
        self._root_finder = root_finder

    def _solve(self, state: SolveState) -> float:
        """Hand the interval to SciPy; every evaluation still goes through ``state.f``, so it is counted and capped."""
        a, b = float(state.interval.a), float(state.interval.b)
        x, _ = self._root_finder(lambda x: float(state.f(x)), a, b, xtol=float(state.xtol), full_output=True)
        return x
