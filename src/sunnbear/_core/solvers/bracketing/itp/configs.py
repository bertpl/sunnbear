"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigsDeclaration, SolverRole

from .solver import ITP
from .variant import ITPVariant


class ITPConfigsDeclaration(SolverConfigsDeclaration):
    """`ITPConfigsDeclaration` declares the configs of `ITP`, which differ in projection radius and in ``n_slack``.

    - ``itp[n_slack=0,variant='paper_experiments']``, the core config: the settings of the paper's experiments and of
      the authors' code;
    - ``itp[n_slack=0,variant='paper_pseudocode']``, a secondary config: the projection radius of the paper's
      pseudocode;
    - ``itp[n_slack=4,variant='paper_experiments']``, a secondary config: the core config with 4 iterations of slack.

    Section V.c of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles, and for ``n_slack = 4``.
    """

    configs = (
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_CORE,
            solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_EXPERIMENTS},
        ),
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_PSEUDOCODE},
        ),
        SolverConfig(
            solver_cls=ITP,
            role=SolverRole.BUILTIN_SECONDARY,
            solver_kwargs={"n_slack": 4, "variant": ITPVariant.PAPER_EXPERIMENTS},
        ),
    )
