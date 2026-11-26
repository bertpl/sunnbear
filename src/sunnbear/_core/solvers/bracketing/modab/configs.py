"""This module declares the built-in configs of `ModAB` and `ModABSafeguarded`, 1 per class."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .modab import ModAB
from .modab_safeguarded import ModABSafeguarded


class ModABConfigsDeclaration(SolverConfigsDeclaration):
    """`ModABConfigsDeclaration` declares the configs of `ModAB` and `ModABSafeguarded`, 1 per class.

    - ``modab``, a secondary config: the method of Ganchovski et al. (2026);
    - ``modab_safeguarded``, a secondary config: the safeguarded method of Tomov and Ganchovski (2026).

    Section V.d of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    configs = (
        SolverConfig(
            solver_cls=ModAB,
            role=SolverRole.BUILTIN_SECONDARY,
            readable_name="modAB",
            summary=(
                "The modified Anderson-Björck method of Ganchovski et al. (2026), which switches between "
                "bisection and the Anderson-Björck method, ported from the article's C# code."
            ),
        ),
        SolverConfig(
            solver_cls=ModABSafeguarded,
            role=SolverRole.BUILTIN_SECONDARY,
            readable_name="modAB, safeguarded",
            summary=(
                "The safeguarded modified Anderson-Björck method of Tomov and Ganchovski (2026), which corrects 2 "
                "defects of the modAB code and changes its rule for falling back to bisection, ported from the "
                "authors' C# code."
            ),
        ),
    )
