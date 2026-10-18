"""This module declares the built-in config of `ModAB`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import ModAB


class ModABConfigs(SolverConfigs):
    """`ModABConfigs` declares the only config of `ModAB`, ``modab``, a secondary config.

    It is not core because the method is not established yet (published 2026), and the evidence for it so far comes from
    its authors' own benchmarks.
    """

    solver_cls = ModAB
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
