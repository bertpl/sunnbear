"""This module declares the built-in configs of `RegulaFalsi`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import RegulaFalsi


class RegulaFalsiConfig(SolverConfig):
    """`RegulaFalsiConfig` is reported for information only.

    The classic method stalls too often to characterize the test functions reliably.
    """

    solver_cls = RegulaFalsi
    role = SolverRole.BUILTIN_SECONDARY
