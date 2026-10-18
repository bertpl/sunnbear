"""This module declares the built-in config of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Bisection


class BisectionConfigs(SolverConfigs):
    """`BisectionConfigs` declares the only config of `Bisection`, ``bisection``, the baseline config.

    Its evaluation count is the benchmark's reference cost.
    """

    solver_cls = Bisection
    configs = (SolverConfig(role=SolverRole.BUILTIN_BASELINE),)
