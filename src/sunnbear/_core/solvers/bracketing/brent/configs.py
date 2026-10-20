"""This module declares the built-in config of `Brent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Brent


class BrentConfigsDeclaration(SolverConfigsDeclaration):
    """`BrentConfigsDeclaration` declares `Brent`'s only config, named ``brent``.

    It is a core config. Brent's method is the de facto standard bracketing solver.
    """

    configs = (SolverConfig(solver_cls=Brent, role=SolverRole.BUILTIN_CORE),)
