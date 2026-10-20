"""This module declares the built-in config of `RegulaFalsi`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import RegulaFalsi


class RegulaFalsiConfigsDeclaration(SolverConfigsDeclaration):
    """`RegulaFalsiConfigsDeclaration` declares `RegulaFalsi`'s only config, named ``regula_falsi``.

    It is a secondary config. It is not core because the classic method stalls too often to characterize the test
    functions reliably.
    """

    configs = (SolverConfig(solver_cls=RegulaFalsi, role=SolverRole.BUILTIN_SECONDARY),)
