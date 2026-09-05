"""A `Solver` around a `scipy.optimize` routine, for agreement tests against the reference solvers.

SciPy owns the loop; the wrapper contributes what `Solver.solve` always does:
evaluation counting, the budget, the guards. SciPy runs on plain floats, so a
twin reports empty flop counts and no iteration count, and exists only to
compare ``x`` and ``n_fevals``. SciPy re-evaluates the endpoints the template
method already evaluated, so a twin's ``n_fevals`` runs two above the
routine's own count.
"""

from collections.abc import Callable

from sunnbear.solvers import Solver, SolveRun


class ScipySolver(Solver):
    """`ScipySolver` runs one `scipy.optimize` bracketing routine under the `Solver` template method."""

    name = "scipy"
    version = 1

    def __init__(self, routine: Callable[..., float]) -> None:
        self.routine = routine

    def _solve(self, run: SolveRun) -> float:
        # SciPy inspects the returned value with numpy, which CountedFloat refuses, so SciPy sees plain floats.
        # Its own maxiter stays out of the way: the wrapper's budget is the one that ends a solve.
        return self.routine(
            lambda x: float(run.f(x)), float(run.bracket.a), float(run.bracket.b), xtol=run.xtol, maxiter=10_000
        )
