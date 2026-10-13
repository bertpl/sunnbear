"""This module declares the built-in configs of `Ridders`, 1 per variant."""

from sunnbear._core.solvers.core import SolverConfig, SolverRole

from .solver import Ridders
from .variant import RiddersVariant


class RiddersScipyConfig(SolverConfig):
    """`RiddersScipyConfig` is a core config: `Ridders` in SciPy's variant.

    Its evaluation count follows how fast the method converges on a function, so its results characterize the test
    functions, and its returned x-value always lies within ``xtol`` of a root.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.SCIPY}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_CORE


class RiddersCommonsMathConfig(SolverConfig):
    """`RiddersCommonsMathConfig` is a secondary config: `Ridders` in Apache Commons Math's variant.

    It is not core because its returned x-value can lie more than ``xtol`` from a root, as on a function with a kink
    or with a multiple root, and such a sample counts as ``max_fevals`` evaluations.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.COMMONS_MATH}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY


class RiddersBracketingSolverConfig(SolverConfig):
    """`RiddersBracketingSolverConfig` is a secondary config: `Ridders` with `BracketingSolver`'s criterion.

    It is not core because this variant does not limit the step as the SciPy variant does, so near the root the
    interval often only halves, and the evaluation count of this config varies widely between near-identical functions.
    """

    solver_cls = Ridders
    solver_kwargs = {"variant": RiddersVariant.BRACKETING_SOLVER}  # noqa: RUF012 — the dict is never mutated
    role = SolverRole.BUILTIN_SECONDARY
