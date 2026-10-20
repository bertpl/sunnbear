"""This module declares the built-in configs of `Ridders`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import Ridders
from .variant import RiddersVariant


class RiddersConfigsDeclaration(SolverConfigsDeclaration):
    """`RiddersConfigsDeclaration` declares the configs of `Ridders`, 1 per variant.

    - ``ridders[variant='standard_stopping_criterion']``, the core config: the paper's steps, with the shared stopping
      criterion;
    - ``ridders[variant='scipy']``, a secondary config: SciPy's step limit and stopping criterion;
    - ``ridders[variant='commons_math']``, a secondary config: Apache Commons Math's stopping criterion.

    Section V.a of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles. Under **Limit on the step**, the docstring of `Ridders` states why the evaluation counts of the core
    config vary more between near-identical functions than those of ``ridders[variant='scipy']``.
    """

    configs = (
        SolverConfig(
            solver_cls=Ridders,
            role=SolverRole.BUILTIN_CORE,
            solver_kwargs={"variant": RiddersVariant.STANDARD_STOPPING_CRITERION},
        ),
        SolverConfig(
            solver_cls=Ridders, role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": RiddersVariant.SCIPY}
        ),
        SolverConfig(
            solver_cls=Ridders,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": RiddersVariant.COMMONS_MATH},
        ),
    )
