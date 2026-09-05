"""`ScipySolver` wraps a `scipy.optimize` routine as a `Solver`, for agreement tests against the reference solvers.

SciPy owns the loop; the `Solver` template method supplies the rest. SciPy runs
on plain floats, so a `ScipySolver` reports empty flop counts and no iteration
count, and exists only to compare ``x`` and ``n_fevals``. SciPy re-evaluates
the endpoints the template method already evaluated, so its ``n_fevals`` runs
two above the routine's own count.
"""

from collections.abc import Callable

from sunnbear.solvers import Solver, SolveRun


class ScipySolver(Solver):
    """A `ScipySolver` runs one `scipy.optimize` bracketing routine under the `Solver` template method."""

    name = "scipy"
    version = 1

    def __init__(self, routine: Callable[..., float]) -> None:
        self.routine = routine

    def _solve(self, run: SolveRun) -> float:
        # SciPy inspects the returned value with numpy, which CountedFloat refuses, so SciPy sees plain floats.
        # maxiter is set high so the wrapper's evaluation budget ends a solve, not SciPy's iteration cap.
        return self.routine(
            lambda x: float(run.f(x)), float(run.bracket.a), float(run.bracket.b), xtol=run.xtol, maxiter=10_000
        )
