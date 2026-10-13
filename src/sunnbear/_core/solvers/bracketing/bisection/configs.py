"""This module declares the built-in configs of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Bisection


class BisectionConfig(SolverConfig):
    """`BisectionConfig` is the baseline config: `Bisection`.

    Its evaluation count is the benchmark's reference cost.
    """

    solver_cls = Bisection
    role = SolverRole.BUILTIN_BASELINE
