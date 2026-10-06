"""This module declares the built-in configs of `Chandrupatla`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Chandrupatla


class ChandrupatlaConfig(SolverConfig):
    """`ChandrupatlaConfig` is a core config, whose results differ from those of Brent's method at a multiple root.

    There, interpolation converges slowly, and Chandrupatla's method switches to bisection while Brent's method keeps
    interpolating.
    """

    solver_cls = Chandrupatla
    role = SolverRole.BUILTIN_CORE
