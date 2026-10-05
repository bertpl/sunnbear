"""This module holds `TWIN_CASES`, the solves that every solver and its twin both run."""

from collections.abc import Callable
from dataclasses import dataclass

from sunnbear.solvers import Solver, SolveResult
from tests.solvers.example_functions import cubic, decreasing_cubic, quintic, steep_exponential

# A budget that no twin case reaches: a solve that hits it ends as MAX_FEVALS, which fails the agreement check.
_MAX_FEVALS = 200


@dataclass(frozen=True)
class TwinCase:
    """A `TwinCase` is 1 solve that a solver and its twin both run: a function, its interval, and the tolerance."""

    f: Callable[[float], float]
    a: float
    b: float
    xtol: float

    def __str__(self) -> str:
        """Return a short label for the test id, e.g. ``cubic[1.0,2.0]@1e-10``."""
        return f"{self.f.__name__}[{self.a},{self.b}]@{self.xtol:g}"

    @property
    def scale(self) -> float:
        """Return the magnitude of the interval bounds, against which `ulps_apart` measures iterates."""
        return max(abs(self.a), abs(self.b))

    def solve(self, solver: Solver) -> SolveResult:
        """Run ``solver`` on this case, with its history recorded, under a budget that no twin case reaches."""
        return solver.solve(self.f, self.a, self.b, xtol=self.xtol, max_fevals=_MAX_FEVALS, history_enabled=True)


TWIN_CASES = [
    TwinCase(f, a, b, xtol)
    for f, a, b in [
        (cubic, 1.0, 2.0),
        (decreasing_cubic, 1.0, 2.0),  # This case has a decreasing function.
        (quintic, 0.0, 1.0),
        (cubic, 1.3, 4.0),  # This case has its root close to the lower bound.
        (steep_exponential, 0.0, 1.0),
    ]
    for xtol in (1e-4, 1e-10)
]
