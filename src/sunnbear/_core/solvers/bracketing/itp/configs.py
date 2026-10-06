"""This module declares the built-in configs of `ITP`: 2 of its robust form, and the form that the paper publishes."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ITP


class ITPRobustSlack4Config(SolverConfig):
    """`ITPRobustSlack4Config` is a core config: `ITP` in its robust form, with ``n_slack = 4``.

    The 4 iterations of slack let the method take interpolation steps that do not halve the interval before the
    projection starts to restrict them, so its evaluation count follows how fast interpolation converges on a
    function.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 4, "is_robust": True}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class ITPRobustSlack0Config(SolverConfig):
    """`ITPRobustSlack0Config` is `ITP` in its robust form, with ``n_slack = 0``, reported for information.

    It is the setting of the paper's experiments, which the authors' MATLAB code ran.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "is_robust": True}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class ITPPublishedConfig(SolverConfig):
    """`ITPPublishedConfig` is `ITP` as the paper's pseudocode states it, reported for information.

    It has ``n_slack = 0``, as in the paper's experiments, and leaves out the robust form.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "is_robust": False}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
