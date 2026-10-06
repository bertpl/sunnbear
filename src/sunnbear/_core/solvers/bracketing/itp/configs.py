"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ITP


class ITPRobustSlack4Config(SolverConfig):
    """`ITPRobustSlack4Config` is a core config: `ITP` in its robust form, with ``n_slack = 4``.

    With 4 iterations allowed beyond the iteration count of bisection, the method can take interpolation steps that
    do not halve the interval before the projection restricts them, so the method's evaluation count follows how fast
    interpolation converges on a function.
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

    It differs from `ITPRobustSlack0Config` only in leaving out the robust form, so rounding errors in the projection
    radius make it go past ``n_max`` more often.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "is_robust": False}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
