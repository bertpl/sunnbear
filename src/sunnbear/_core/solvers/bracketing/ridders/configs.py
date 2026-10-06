"""This module declares the built-in configs of `Ridders`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Ridders


class RiddersScipyConfig(SolverConfig):
    """`RiddersScipyConfig` is `Ridders` in SciPy's variant, a core config.

    Its evaluation count follows how fast the method converges on a function, and its root always lies within
    ``xtol`` of the true root.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": "scipy"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class RiddersCommonsMathConfig(SolverConfig):
    """`RiddersCommonsMathConfig` is `Ridders` in Apache Commons Math's variant, reported for information.

    On a function that is not smooth, its root often lies more than ``xtol`` from the true root, and such a sample
    counts as ``max_fevals`` evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": "commons_math"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class RiddersBracketingSolverConfig(SolverConfig):
    """`RiddersBracketingSolverConfig` is `Ridders` with `BracketingSolver`'s criterion, reported for information.

    Without SciPy's limit on the step, the interval often only halves near the root, so its evaluation count varies
    widely between near-identical functions.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": "bracketing_solver"}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
