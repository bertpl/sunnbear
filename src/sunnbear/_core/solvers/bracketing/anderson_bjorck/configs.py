"""This module declares the built-in config of `AndersonBjorck`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import AndersonBjorck


class AndersonBjorckConfigsDeclaration(SolverConfigsDeclaration):
    """`AndersonBjorckConfigsDeclaration` declares `AndersonBjorck`'s only config, named ``anderson_bjorck``.

    It is a secondary config. It is not core because the config of `Illinois` already represents the modified regula
    falsi family among the core configs.
    """

    solver_cls = AndersonBjorck
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
