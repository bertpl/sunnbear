"""This module declares the built-in configs of `Pegasus`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Pegasus


class PegasusConfig(SolverConfig):
    """`PegasusConfig` is a secondary config.

    `IllinoisConfig` already represents the modified regula falsi family among the core configs.
    """

    solver_cls = Pegasus
    role = SolverRole.BUILTIN_SECONDARY
