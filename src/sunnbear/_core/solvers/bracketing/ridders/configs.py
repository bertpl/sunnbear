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
            readable_name="Ridders",
            summary=(
                r"Ridders' method (Ridders, 1979), which ends once the interval is at most $2 \cdot "
                r"x_{\text{tol}}$ wide, the stopping criterion of sunnbear's bracketing solvers."
            ),
        ),
        SolverConfig(
            solver_cls=Ridders,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": RiddersVariant.SCIPY},
            readable_name="Ridders (SciPy stopping)",
            summary=(
                "Ridders' method with the step limit and the stopping criterion of SciPy's ridder: it ends once "
                r"the interval is narrower than $x_{\text{tol}}$, and returns the last evaluated x-value."
            ),
        ),
        SolverConfig(
            solver_cls=Ridders,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": RiddersVariant.COMMONS_MATH},
            readable_name="Ridders (ACM stopping)",
            summary=(
                "Ridders' method with the stopping criterion of Apache Commons Math's RiddersSolver: it ends once "
                r"2 successive iterates lie at most $x_{\text{tol}}$ apart, and returns the last evaluated "
                "x-value."
            ),
        ),
    )
