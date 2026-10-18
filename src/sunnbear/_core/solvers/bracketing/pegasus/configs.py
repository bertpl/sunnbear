"""This module declares the built-in config of `Pegasus`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Pegasus


class PegasusConfigs(SolverConfigs):
    """`PegasusConfigs` declares the only config of `Pegasus`, ``pegasus``, a secondary config.

    It is not core because the config of `Illinois` already represents the modified regula falsi family among the core
    configs.
    """

    solver_cls = Pegasus
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
