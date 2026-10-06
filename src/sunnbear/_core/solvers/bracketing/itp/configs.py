"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ITP


class ITPPaperExperimentsSlack4Config(SolverConfig):
    """`ITPPaperExperimentsSlack4Config` is a core config: `ITP` in its paper's experiments variant, ``n_slack = 4``.

    With ``n_slack = 4``, the projection accepts interpolation steps that shrink the interval by less than half, as
    long as the solve can still end within 4 iterations more than bisection, so the evaluation count depends on how
    fast interpolation converges on the function.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 4, "variant": "paper_experiments"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class ITPPaperExperimentsSlack0Config(SolverConfig):
    """`ITPPaperExperimentsSlack0Config` is `ITP` in its paper's experiments variant, ``n_slack = 0``, for information.

    It is the setting of the paper's experiments.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "variant": "paper_experiments"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class ITPPaperPseudocodeSlack0Config(SolverConfig):
    """`ITPPaperPseudocodeSlack0Config` is `ITP` as its paper's pseudocode states it, reported for information.

    It differs from `ITPPaperExperimentsSlack0Config` only in its projection radius, which has no margin, so its solves
    go past the iteration bound ``n_max`` of `ITP` more often, and end as pure bisection once their slack runs out.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "variant": "paper_pseudocode"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
