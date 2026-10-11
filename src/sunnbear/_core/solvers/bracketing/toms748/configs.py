"""This module declares the built-in configs of `TOMS748`, 1 per value of ``k``."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import TOMS748


class TOMS748K1Config(SolverConfig):
    """`TOMS748K1Config` is `TOMS748` with ``k = 1``, the paper's Algorithm 4.1.

    It is reported for information: ``k = 1`` is the default of SciPy's ``toms748``.
    """

    solver_cls = TOMS748
    solver_kwargs = {"k": 1}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class TOMS748K2Config(SolverConfig):
    """`TOMS748K2Config` is a core config: `TOMS748` with ``k = 2``, the paper's Algorithm 4.2.

    ``k = 2`` is the core config, not ``k = 1``: the authors' code implements only Algorithm 4.2, and the paper's
    Table II gives Algorithm 4.2 fewer evaluations than Algorithm 4.1.
    """

    solver_cls = TOMS748
    solver_kwargs = {"k": 2}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE
