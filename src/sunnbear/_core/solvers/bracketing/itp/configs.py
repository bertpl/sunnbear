"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import ITP
from .variant import ITPVariant


class ITPConfigs(SolverConfigs):
    """`ITPConfigs` declares the configs of `ITP`, which differ in their projection radius and in ``n_slack``.

    - ``itp[n_slack=0,variant='paper_experiments']``, the core config: the settings of the paper's experiments and of
      the authors' code;
    - ``itp[n_slack=0,variant='paper_pseudocode']``, a secondary config: the projection radius of the paper's
      pseudocode;
    - ``itp[n_slack=4,variant='paper_experiments']``, a secondary config: the core config with 4 iterations of slack.

    Section V.c of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles, and for ``n_slack = 4``.
    """

    solver_cls = ITP
    configs = (
        SolverConfig(
            role=SolverRole.BUILTIN_CORE, solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_EXPERIMENTS}
        ),
        SolverConfig(
            role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"n_slack": 0, "variant": ITPVariant.PAPER_PSEUDOCODE}
        ),
        SolverConfig(
            role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"n_slack": 4, "variant": ITPVariant.PAPER_EXPERIMENTS}
        ),
    )
