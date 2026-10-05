"""This module declares the built-in configs of `Illinois`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Illinois


class IllinoisConfig(SolverConfig):
    """`IllinoisConfig` is a core config: its results characterize the test functions.

    It represents the regula falsi variants that scale the function value at the bound that the interval keeps.
    """

    solver_cls = Illinois
    role = SolverRole.BUILTIN_CORE
