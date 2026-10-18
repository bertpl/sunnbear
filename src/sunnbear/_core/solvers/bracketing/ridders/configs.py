"""This module declares the built-in configs of `Ridders`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Ridders
from .variant import RiddersVariant


class RiddersStandardStoppingCriterionConfig(SolverConfig):
    """`RiddersStandardStoppingCriterionConfig` is the core config of `Ridders`, with the steps that the paper states.

    The paper states no stopping criterion, so this config uses the shared stopping criterion of the bracketing
    solvers, and checks it where SciPy's ``ridder`` checks its own.

    This config's evaluation counts can vary between near-identical functions; the docstring of `Ridders` states why,
    under **Limit on the step**.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.STANDARD_STOPPING_CRITERION}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class RiddersScipyConfig(SolverConfig):
    """`RiddersScipyConfig` is a secondary config of `Ridders`, in SciPy's variant.

    It shows the stopping criterion of SciPy's ``ridder``. That criterion is not the shared stopping criterion of the
    bracketing solvers, so this config is not core.

    Its evaluation counts vary less between near-identical functions than those of
    `RiddersStandardStoppingCriterionConfig`; the docstring of `Ridders` states why, under **Limit on the step**.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.SCIPY}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class RiddersCommonsMathConfig(SolverConfig):
    """`RiddersCommonsMathConfig` is a secondary config of `Ridders`, in Apache Commons Math's variant.

    It shows the stopping criterion of Apache Commons Math's ``RiddersSolver``. That criterion is not the shared
    stopping criterion of the bracketing solvers, so this config is not core.

    Its returned x-value can lie more than ``xtol`` from a root, as on a function with a kink or with a multiple root,
    and the benchmark counts such a solve as failed, at ``max_fevals`` evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.COMMONS_MATH}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
