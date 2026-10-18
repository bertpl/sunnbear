"""This module declares the built-in configs of `TOMS748`, 1 per value of ``k``."""

from sunnbear._core.solvers.core import SolverConfig, SolverConfigs, SolverRole

from .solver import TOMS748


class TOMS748Configs(SolverConfigs):
    """`TOMS748Configs` declares the configs of `TOMS748`, 1 per value of ``k``.

    - ``toms748[k=2]``, the core config: the paper's Algorithm 4.2;
    - ``toms748[k=1]``, a secondary config: the paper's Algorithm 4.1.

    Section V.b of ``SOLVER_IMPLEMENTATIONS.md``, in the package `sunnbear._core.solvers`, gives the reasons for the
    configs' roles.
    """

    solver_cls = TOMS748
    configs = (
        SolverConfig(role=SolverRole.BUILTIN_CORE, solver_kwargs={"k": 2}),
        SolverConfig(role=SolverRole.BUILTIN_SECONDARY, solver_kwargs={"k": 1}),
    )
