"""This module declares the built-in config of `Illinois`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Illinois


class IllinoisConfigs(SolverConfigs):
    """`IllinoisConfigs` declares the only config of `Illinois`, ``illinois``, a core config.

    Unlike `RegulaFalsi`, `Illinois` does not stall on a convex or concave function, so its results characterize the
    test functions.
    """

    solver_cls = Illinois
    configs = (SolverConfig(role=SolverRole.BUILTIN_CORE),)
