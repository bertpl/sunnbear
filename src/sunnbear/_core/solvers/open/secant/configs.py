"""This module declares the built-in config of `Secant`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import Secant


class SecantConfigs(SolverConfigs):
    """`SecantConfigs` declares `Secant`'s only config, a secondary config named ``secant``.

    It is not core because the secant method can stop at an incorrect x-value or leave the interval, so its results do
    not reliably characterize the test functions.
    """

    solver_cls = Secant
    configs = (SolverConfig(role=SolverRole.BUILTIN_SECONDARY),)
