"""This module declares the built-in config of `SteffenBrent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import SteffenBrent


class SteffenBrentConfigsDeclaration(SolverConfigsDeclaration):
    """`SteffenBrentConfigsDeclaration` declares `SteffenBrent`'s only config, named ``steffen_brent``.

    It is a secondary config. It is not core because the method is not established yet (published 2025), and its paper
    tests it on 2 functions only.
    """

    solver_cls = SteffenBrent
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
