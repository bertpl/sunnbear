"""This module declares the built-in config of `Chandrupatla`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Chandrupatla


class ChandrupatlaConfigs(SolverConfigs):
    """`ChandrupatlaConfigs` declares `Chandrupatla`'s only config, a core config named ``chandrupatla``.

    Its results differ from those of Brent's method at a multiple root. There, interpolation converges slowly, and
    Chandrupatla's method switches to bisection while Brent's method keeps interpolating.
    """

    solver_cls = Chandrupatla
    configs = (SolverConfig(role=SolverRole.BUILTIN_CORE),)
