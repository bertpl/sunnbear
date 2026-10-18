"""This module declares the built-in config of `Brent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Brent


class BrentConfigs(SolverConfigs):
    """`BrentConfigs` declares the only config of `Brent`, ``brent``, a core config.

    Brent's method is the de facto standard bracketing solver.
    """

    solver_cls = Brent
    configs = (SolverConfig(role=SolverRole.BUILTIN_CORE),)
