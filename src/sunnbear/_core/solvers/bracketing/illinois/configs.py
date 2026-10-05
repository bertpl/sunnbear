"""This module declares the built-in configs of `Illinois`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Illinois


class IllinoisConfig(SolverConfig):
    """`IllinoisConfig` is a core config.

    Unlike `RegulaFalsiConfig`, its solver does not stall on a convex or concave function, so its results
    characterize the test functions.
    """

    solver_cls = Illinois
    role = SolverRole.BUILTIN_CORE
