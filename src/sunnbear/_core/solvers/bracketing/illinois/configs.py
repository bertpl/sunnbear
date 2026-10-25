"""This module declares the built-in config of `Illinois`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Illinois


class IllinoisConfigsDeclaration(SolverConfigsDeclaration):
    """`IllinoisConfigsDeclaration` declares `Illinois`'s only config, named ``illinois``.

    It is a core config. Unlike `RegulaFalsi`, `Illinois` does not stall on a convex or concave function, so its results
    characterize the test problems.
    """

    configs = (SolverConfig(solver_cls=Illinois, role=SolverRole.BUILTIN_CORE),)
