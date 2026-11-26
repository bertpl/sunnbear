"""This module declares the built-in config of `AndersonBjorck`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import AndersonBjorck


class AndersonBjorckConfigsDeclaration(SolverConfigsDeclaration):
    """`AndersonBjorckConfigsDeclaration` declares `AndersonBjorck`'s only config, named ``anderson_bjorck``.

    It is a secondary config. It is not core because the config of `Illinois` already represents the modified regula
    falsi family among the core configs.
    """

    configs = (
        SolverConfig(
            solver_cls=AndersonBjorck,
            role=SolverRole.BUILTIN_SECONDARY,
            readable_name="Anderson-Björck",
            summary=(
                "The method of Anderson and Björck (1973): regula falsi that multiplies the function value of an "
                r"interval bound that it keeps twice in a row by $1 - f_{\text{new}} / f_{\text{previous}}$, or by "
                "0.5 where that is not positive."
            ),
        ),
    )
