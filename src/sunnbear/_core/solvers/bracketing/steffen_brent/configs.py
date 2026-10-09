"""This module declares the built-in configs of `SteffenBrent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import SteffenBrent


class SteffenBrentConfig(SolverConfig):
    """`SteffenBrentConfig` is a secondary config.

    It is not core because the method is recent, and its paper tests it on 2 functions only.
    """

    solver_cls = SteffenBrent
    role = SolverRole.BUILTIN_SECONDARY
