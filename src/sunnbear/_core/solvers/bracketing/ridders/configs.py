"""This module declares the built-in configs of `Ridders`, 1 per stopping criterion."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Ridders


class RiddersOriginalCriterionConfig(SolverConfig):
    """`RiddersOriginalCriterionConfig` is `Ridders` with its original stopping criterion, a core config.

    Its evaluation count follows how fast the method converges on a function, so its results characterize the test
    functions. A sample whose root lies more than ``xtol`` from the true root counts as ``max_fevals`` evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"stopping_criterion": "original"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class RiddersCorrectedCriterionConfig(SolverConfig):
    """`RiddersCorrectedCriterionConfig` is `Ridders` with its corrected stopping criterion, reported for information.

    Its roots are always accurate, but its evaluation count varies unpredictably between near-identical functions, so
    its results characterize the test functions less well than those of the original criterion.
    """

    solver_cls = Ridders
    solver_kwargs = {"stopping_criterion": "corrected"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
