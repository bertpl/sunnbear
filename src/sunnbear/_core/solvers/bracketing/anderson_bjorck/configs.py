"""This module declares the built-in configs of `AndersonBjorck`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import AndersonBjorck


class AndersonBjorckConfig(SolverConfig):
    """`AndersonBjorckConfig` is a secondary config.

    It is not core because `IllinoisConfig` already represents the modified regula falsi family among the core
    configs.
    """

    solver_cls = AndersonBjorck
    role = SolverRole.BUILTIN_SECONDARY
