"""This module declares the built-in configs of `TOMS748`, 1 per value of ``k``."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import TOMS748


class TOMS748K1Config(SolverConfig):
    """`TOMS748K1Config` is a core config: `TOMS748` with ``k = 1``, the paper's Algorithm 4.1.

    ``k = 1`` is the core config, not ``k = 2``: it is the default of SciPy's ``toms748``, and over a broad range of
    functions it needs significantly fewer evaluations on average, although ``k = 2`` needs about 2 % fewer on the
    paper's smooth test problems. Its evaluation counts therefore tell apart the difficulty of a broader range of test
    functions.
    """

    solver_cls = TOMS748
    solver_kwargs = {"k": 1}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class TOMS748K2Config(SolverConfig):
    """`TOMS748K2Config` is a secondary config: `TOMS748` with ``k = 2``, the paper's Algorithm 4.2."""

    solver_cls = TOMS748
    solver_kwargs = {"k": 2}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
