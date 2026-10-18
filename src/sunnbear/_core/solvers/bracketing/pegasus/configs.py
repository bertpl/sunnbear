"""This module declares the built-in config of `Pegasus`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Pegasus


class PegasusConfigsDeclaration(SolverConfigsDeclaration):
    """`PegasusConfigsDeclaration` declares `Pegasus`'s only config, named ``pegasus``.

    It is a secondary config. It is not core because the config of `Illinois` already represents the modified regula
    falsi family among the core configs.
    """

    solver_cls = Pegasus
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
