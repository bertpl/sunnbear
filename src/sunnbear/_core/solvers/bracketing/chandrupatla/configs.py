"""This module declares the built-in config of `Chandrupatla`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Chandrupatla


class ChandrupatlaConfigsDeclaration(SolverConfigsDeclaration):
    """`ChandrupatlaConfigsDeclaration` declares `Chandrupatla`'s only config, named ``chandrupatla``.

    It is a core config. Its results differ from those of Brent's method at a multiple root. There, interpolation
    converges slowly, and Chandrupatla's method switches to bisection while Brent's method keeps interpolating.
    """

    configs = (
        SolverConfig(
            solver_cls=Chandrupatla,
            role=SolverRole.BUILTIN_CORE,
            readable_name="Chandrupatla",
            summary=(
                "Chandrupatla's method (Chandrupatla, 1997), as the BASIC listing of its article: inverse "
                "quadratic interpolation where the article shows it to be well conditioned, and bisection "
                "everywhere else."
            ),
        ),
    )
