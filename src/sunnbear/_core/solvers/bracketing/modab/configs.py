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
        SolverConfig(solver_cls=ModAB, role=SolverRole.BUILTIN_SECONDARY),
        SolverConfig(solver_cls=ModABSafeguarded, role=SolverRole.BUILTIN_SECONDARY),
    )
