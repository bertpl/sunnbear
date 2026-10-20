"""This module declares the built-in config of `CARF`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import CARF


class CARFConfigsDeclaration(SolverConfigsDeclaration):
    """`CARFConfigsDeclaration` declares `CARF`'s only config, named ``carf``.

    It is a secondary config, with the paper's constants. It is not core because the method is not established yet
    (published 2026), and `CARF` reconstructs it from the paper's description, without the author's code.
    """

    configs = (SolverConfig(solver_cls=CARF, role=SolverRole.BUILTIN_SECONDARY),)
