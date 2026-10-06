"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ITP


class ITPRobustSlack4Config(SolverConfig):
    """`ITPRobustSlack4Config` is a core config: `ITP` in its robust form, with ``n_slack = 4``.

    With ``n_slack = 4``, the projection accepts interpolation steps that shrink the interval by less than half, as
    long as the solve can still end within 4 iterations more than bisection, so the evaluation count depends on how
    fast interpolation converges on the function.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 4, "is_robust": True}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class ITPRobustSlack0Config(SolverConfig):
    """`ITPRobustSlack0Config` is `ITP` in its robust form, with ``n_slack = 0``, reported for information.

    The paper's experiments used this setting, and ran it with the authors' MATLAB code.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "is_robust": True}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class ITPPublishedSlack0Config(SolverConfig):
    """`ITPPublishedSlack0Config` is `ITP` as the paper's pseudocode states it, reported for information.

    It differs from `ITPRobustSlack0Config` only in leaving out the correction of the projection radius for rounding
    errors, so its solves go past the iteration bound ``n_max`` of `ITP` more often.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "is_robust": False}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
