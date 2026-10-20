"""This module declares the built-in configs of `ModAB`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import ModAB
from .variant import ModABVariant


class ModABConfigsDeclaration(SolverConfigsDeclaration):
    """`ModABConfigsDeclaration` declares the configs of `ModAB`, 1 per variant.

    - ``modab[variant='algorithms_2026']``, a secondary config: the method of Ganchovski et al. (2026);
    - ``modab[variant='safeguarded_2026']``, a secondary config: the safeguarded method of Tomov and Ganchovski
      (2026).

    Section V.d of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    configs = (
        SolverConfig(
            solver_cls=ModAB, role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"variant": ModABVariant.ALGORITHMS_2026}
        ),
        SolverConfig(
            solver_cls=ModAB,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"variant": ModABVariant.SAFEGUARDED_2026},
        ),
    )
