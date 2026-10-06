"""This module declares the built-in configs of `Secant`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Secant


class SecantConfig(SolverConfig):
    """`SecantConfig` is a secondary config.

    It is not core because the secant method can stop at an incorrect point or leave the interval, so its results
    do not reliably characterize the test functions.
    """

    solver_cls = Secant
    role = SolverRole.BUILTIN_SECONDARY
