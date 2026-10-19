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

    solver_cls = Ford
    configs = (
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": FordVariant.METHOD_1}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": FordVariant.METHOD_3}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": FordVariant.METHOD_4}),
    )
