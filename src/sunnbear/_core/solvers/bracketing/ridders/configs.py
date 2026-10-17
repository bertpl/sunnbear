"""This module declares the built-in configs of `Ridders`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Ridders
from .variant import RiddersVariant


class RiddersBracketingSolverConfig(SolverConfig):
    """`RiddersBracketingSolverConfig` is the core config of `Ridders`, with Ridders' steps as the paper states them.

    The paper states no stopping criterion, so this config fills that gap with the stopping criterion that all
    bracketing solvers share, and checks it where SciPy's ``ridder`` checks its own.

    Near the root, a new iterate can land between the root and the far bound, and the interval then only halves, so
    this config's evaluation counts can vary between near-identical functions.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.BRACKETING_SOLVER}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class RiddersScipyConfig(SolverConfig):
    """`RiddersScipyConfig` is a secondary config of `Ridders`, in SciPy's variant.

    It shows the stopping criterion of SciPy's ``ridder``. That criterion is not the one that all bracketing solvers
    share, so this config is not core.

    It also limits each step so that the new iterate lies at least ``xtol/2`` inside the interval, which the paper does
    not state; near the root, that limit shrinks the interval to the stopping width in fewer evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.SCIPY}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class RiddersCommonsMathConfig(SolverConfig):
    """`RiddersCommonsMathConfig` is a secondary config of `Ridders`, in Apache Commons Math's variant.

    It shows the stopping criterion of Apache Commons Math's ``RiddersSolver``. That criterion is not the one that all
    bracketing solvers share, so this config is not core.

    Its returned x-value can lie more than ``xtol`` from a root, as on a function with a kink or with a multiple root,
    and such a sample counts as ``max_fevals`` evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.COMMONS_MATH}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
