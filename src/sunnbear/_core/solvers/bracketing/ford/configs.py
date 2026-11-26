"""This module declares the built-in configs of `Ford`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Ford
from .variant import FordVariant


class FordConfigsDeclaration(SolverConfigsDeclaration):
    """`FordConfigsDeclaration` declares the configs of `Ford`, 1 per variant.

    - ``ford[variant='method_1']``, a secondary config: Method 1 of Ford (1997);
    - ``ford[variant='method_3']``, a secondary config: Method 3 of Ford (1997);
    - ``ford[variant='method_4']``, a secondary config: Method 4 of Ford (1997).

    Section V.e of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    configs = (
        SolverConfig(
            solver_cls=Ford,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": FordVariant.METHOD_1},
            readable_name="Ford (Method 1)",
            summary=(
                "Method 1 of Ford (1997): regula falsi that multiplies the function value of an interval bound "
                "that it keeps twice in a row by a ratio of 2 slopes, whose denominator is the slope at the "
                "oldest of the last 3 iterates of the quadratic through them."
            ),
        ),
        SolverConfig(
            solver_cls=Ford,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": FordVariant.METHOD_3},
            readable_name="Ford (Method 3)",
            summary=(
                "Method 3 of Ford (1997): regula falsi that multiplies the function value of an interval bound "
                "that it keeps twice in a row by a ratio of 2 slopes, whose denominator is the slope of the "
                "secant through the oldest and the newest of the last 3 iterates."
            ),
        ),
        SolverConfig(
            solver_cls=Ford,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": FordVariant.METHOD_4},
            readable_name="Ford (Method 4)",
            summary=(
                "Method 4 of Ford (1997): regula falsi that multiplies the function value of an interval bound "
                "that it keeps twice in a row by a ratio of 2 slopes, whose denominator is the slope of the "
                "secant through the oldest 2 of the last 3 iterates."
            ),
        ),
    )
