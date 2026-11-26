"""This module declares the built-in config of `Bisection`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Bisection


class BisectionConfigsDeclaration(SolverConfigsDeclaration):
    """`BisectionConfigsDeclaration` declares `Bisection`'s only config, named ``bisection``.

    It is the baseline config. Its evaluation count is the benchmark's reference cost.
    """

    configs = (
        SolverConfig(
            solver_cls=Bisection,
            role=SolverRole.BUILTIN_BASELINE,
            readable_name="Bisection",
            summary=("Bisection, which splits the interval at its midpoint in every iteration."),
        ),
    )
