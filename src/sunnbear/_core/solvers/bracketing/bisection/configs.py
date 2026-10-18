"""This module declares the built-in config of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Bisection


class BisectionConfigs(SolverConfigs):
    """`BisectionConfigs` declares `Bisection`'s only config, the baseline config named ``bisection``.

    Its evaluation count is the benchmark's reference cost.
    """

    solver_cls = Bisection
    configs = (SolverConfig(role=SolverRole.BUILTIN_BASELINE),)
