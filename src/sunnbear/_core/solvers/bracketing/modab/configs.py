"""This module declares the built-in configs of `ModAB`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ModAB


class ModABConfig(SolverConfig):
    """`ModABConfig` is a secondary config.

    It is not core because the method is recent, and the evidence for it so far comes from its authors' own
    benchmarks.
    """

    solver_cls = ModAB
    role = SolverRole.BUILTIN_SECONDARY
