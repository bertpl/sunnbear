"""`ScipySolver` wraps a `scipy.optimize` routine as a `Solver`, for agreement tests against the reference solvers.

SciPy runs on plain floats, so a `ScipySolver` reports empty flop counts and
no iteration count, and exists only to compare ``x`` and ``n_fevals``. SciPy
re-evaluates the endpoints the template method already evaluated, so its
``n_fevals`` is the routine's own count plus two.
"""

from collections.abc import Callable

from sunnbear.solvers import Solver, SolveRun


class ScipySolver(Solver):
    """A `ScipySolver` hands SciPy the loop and measures only what the `Solver` template method measures."""

    name = "scipy"
    version = 1

    def __init__(self, routine: Callable[..., float]) -> None:
        self.routine = routine

    def _solve(self, run: SolveRun) -> float:
        # SciPy inspects the returned value with numpy, which CountedFloat refuses, so SciPy sees plain floats.
        # maxiter is set high so that max_fevals ends a solve, not SciPy's iteration cap.
        return self.routine(
            lambda x: float(run.f(x)), float(run.bracket.a), float(run.bracket.b), xtol=run.xtol, maxiter=10_000
        )
