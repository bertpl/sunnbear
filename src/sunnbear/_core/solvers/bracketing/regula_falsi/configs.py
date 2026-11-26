"""This module declares the built-in config of `RegulaFalsi`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import RegulaFalsi


class RegulaFalsiConfigsDeclaration(SolverConfigsDeclaration):
    """`RegulaFalsiConfigsDeclaration` declares `RegulaFalsi`'s only config, named ``regula_falsi``.

    It is a secondary config. It is not core because the classic method stalls too often to characterize the test
    problems reliably.
    """

    configs = (
        SolverConfig(
            solver_cls=RegulaFalsi,
            role=SolverRole.BUILTIN_SECONDARY,
            readable_name="Regula Falsi",
            summary=(
                "The classic regula falsi method, which evaluates the zero of the secant through the 2 interval "
                "bounds in every iteration, without any modification against its stall on a convex or concave "
                "function."
            ),
        ),
    )
