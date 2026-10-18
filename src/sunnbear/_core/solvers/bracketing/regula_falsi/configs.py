"""This module declares the built-in config of `RegulaFalsi`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import RegulaFalsi


class RegulaFalsiConfigs(SolverConfigs):
    """`RegulaFalsiConfigs` declares `RegulaFalsi`'s only config, a secondary config named ``regula_falsi``.

    It is not core because the classic method stalls too often to characterize the test functions reliably.
    """

    solver_cls = RegulaFalsi
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
