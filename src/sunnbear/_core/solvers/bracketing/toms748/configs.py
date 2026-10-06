"""This module declares the built-in configs of `TOMS748`, 1 per value of ``k``."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import TOMS748


class TOMS748K1Config(SolverConfig):
    """`TOMS748K1Config` is a core config: `TOMS748` with ``k = 1``, the paper's Algorithm 4.1.

    ``k = 1`` is the core config, not ``k = 2``: on smooth functions ``k = 2`` saves few evaluations, and on harder
    functions it needs many more.
    """

    solver_cls = TOMS748
    solver_kwargs = {"k": 1}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class TOMS748K2Config(SolverConfig):
    """`TOMS748K2Config` is a secondary config: `TOMS748` with ``k = 2``, the paper's Algorithm 4.2."""

    solver_cls = TOMS748
    solver_kwargs = {"k": 2}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
