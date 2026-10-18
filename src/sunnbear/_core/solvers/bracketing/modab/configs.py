"""This module declares the built-in config of `ModAB`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import ModAB


class ModABConfigsDeclaration(SolverConfigsDeclaration):
    """`ModABConfigsDeclaration` declares `ModAB`'s only config, named ``modab``.

    It is a secondary config. It is not core because the method is not established yet (published 2026), and the
    evidence for it so far comes from its authors' own benchmarks.
    """

    solver_cls = ModAB
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
