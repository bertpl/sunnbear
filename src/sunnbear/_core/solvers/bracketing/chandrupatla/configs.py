"""This module declares the built-in config of `Chandrupatla`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Chandrupatla


class ChandrupatlaConfigsDeclaration(SolverConfigsDeclaration):
    """`ChandrupatlaConfigsDeclaration` declares `Chandrupatla`'s only config, named ``chandrupatla``.

    It is a core config. Its results differ from those of Brent's method at a multiple root. There, interpolation
    converges slowly, and Chandrupatla's method switches to bisection while Brent's method keeps interpolating.
    """

    solver_cls = Chandrupatla
    configs = (SolverConfig(role=SolverRole.BUILTIN_CORE),)
