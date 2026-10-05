"""This module declares the built-in configs of `Illinois`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Illinois


class IllinoisConfig(SolverConfig):
    """`IllinoisConfig` characterizes the test functions: it represents the modified regula falsi family."""

    solver_cls = Illinois
    role = SolverRole.BUILTIN_CORE
