"""This module declares the built-in config of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Bisection


class BisectionConfigsDeclaration(SolverConfigsDeclaration):
    """`BisectionConfigsDeclaration` declares `Bisection`'s only config, named ``bisection``.

    It is the baseline config. Its evaluation count is the benchmark's reference cost.
    """

    solver_cls = Bisection
    configs = (SolverConfig(role=SolverRole.BUILTIN_BASELINE),)
