"""This module defines the test-local solver that the solver config tests share.

It also defines a helper that declares configs of that solver.
"""

from sunnbear.solvers import BracketingSolver, Interval, SolverConfig, SolveState


class WeightedSplitSolver(BracketingSolver):
    """`WeightedSplitSolver` splits the interval at a fixed fraction of its width, set through ``__init__``."""

    name = "weighted_split"
    version = 1

    def __init__(self, weight: float, n_warmup: int = 0) -> None:
        self.weight = weight
        self.n_warmup = n_warmup

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        return interval.a + self.weight * interval.width


def define_config(namespace: dict[str, object]) -> type[SolverConfig]:
    """Define, and so register, a config class with the attributes in ``namespace``.

    The class counts as defined in the test suite, outside the sunnbear package, unless ``namespace``
    names another ``__module__``.
    """
    return type("Config", (SolverConfig,), {"__module__": "tests.solvers", **namespace})
