"""This module declares the built-in configs of `Chandrupatla`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Chandrupatla


class ChandrupatlaConfig(SolverConfig):
    """`ChandrupatlaConfig` is a core config.

    Where interpolation converges slowly, as at a multiple root, Chandrupatla's method falls back to bisection where
    Brent's method keeps interpolating, so its results differ from Brent's there.
    """

    solver_cls = Chandrupatla
    role = SolverRole.BUILTIN_CORE
