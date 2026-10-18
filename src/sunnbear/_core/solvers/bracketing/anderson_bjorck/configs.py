"""This module declares the built-in config of `AndersonBjorck`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import AndersonBjorck


class AndersonBjorckConfigs(SolverConfigs):
    """`AndersonBjorckConfigs` declares the only config of `AndersonBjorck`, ``anderson_bjorck``, a secondary config.

    It is not core because the config of `Illinois` already represents the modified regula falsi family among the core
    configs.
    """

    solver_cls = AndersonBjorck
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
