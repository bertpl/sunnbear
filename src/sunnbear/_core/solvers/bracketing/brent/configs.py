"""This module declares the built-in configs of `Brent`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Brent


class BrentConfig(SolverConfig):
    """`BrentConfig` is a core config: Brent's method is the de facto standard bracketing solver."""

    solver_cls = Brent
    role = SolverRole.BUILTIN_CORE
