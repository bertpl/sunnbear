"""This module declares the built-in configs of `ITP`."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import ITP
from .variant import ITPVariant


class ITPPaperExperimentsSlack4Config(SolverConfig):
    """`ITPPaperExperimentsSlack4Config` is a secondary config of `ITP`.

    It runs variant ``"paper_experiments"`` with ``n_slack = 4``. It is not core because
    `ITPPaperExperimentsSlack0Config` is the core config of `ITP`; that config's docstring says why it was chosen.

    With ``n_slack = 4``, the projection accepts interpolation steps that shrink the interval by less than half, as long
    as the solve can still end at most 4 iterations later than bisection would, so the evaluation count depends on how
    fast interpolation converges on the function.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 4, "variant": ITPVariant.PAPER_EXPERIMENTS}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class ITPPaperExperimentsSlack0Config(SolverConfig):
    """`ITPPaperExperimentsSlack0Config` is a core config of `ITP`.

    It runs variant ``"paper_experiments"`` with ``n_slack = 0``. It is the core config because the paper's experiments
    ran `ITP` with this variant and ``n_slack = 0``, and the authors' code uses the same settings.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "variant": ITPVariant.PAPER_EXPERIMENTS}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class ITPPaperPseudocodeSlack0Config(SolverConfig):
    """`ITPPaperPseudocodeSlack0Config` is a secondary config of `ITP`, as its paper's pseudocode states it.

    It is not core because `ITPPaperExperimentsSlack0Config` is the core config of `ITP`; that config's docstring
    says why it was chosen.

    This config differs from `ITPPaperExperimentsSlack0Config` only in its projection radius ``r``, which it does not
    lower to ``max(0.99 * r - xtol / 2, 0)``, so its solves go past the iteration bound ``n_max`` of `ITP` more often,
    and end as pure bisection once their projection radius reaches 0.
    """

    solver_cls = ITP
    solver_kwargs = {"n_slack": 0, "variant": ITPVariant.PAPER_PSEUDOCODE}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
