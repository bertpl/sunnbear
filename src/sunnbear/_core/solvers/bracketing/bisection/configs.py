"""This module declares the built-in configs of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Bisection


class BisectionConfig(SolverConfig):
    """`BisectionConfig` is the benchmark's baseline: its exact evaluation count is the reference cost."""

    solver_cls = Bisection
    role = SolverRole.BUILTIN_BASELINE
