"""This module declares the built-in config of `SteffenBrent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import SteffenBrent


class SteffenBrentConfigs(SolverConfigs):
    """`SteffenBrentConfigs` declares `SteffenBrent`'s only config, a secondary config named ``steffen_brent``.

    It is not core because the method is not established yet (published 2025), and its paper tests it on 2 functions
    only.
    """

    solver_cls = SteffenBrent
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
