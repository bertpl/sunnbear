"""The `Formula` data model: hand-written function families plus generation metadata.

A formula owns three parameter layers with distinct roles: the recipe-swept
``p`` tuple (bound once per test function, consciously shaping its character),
the Monte-Carlo parameter ``c`` (varied per benchmark run), and — downstream,
never stored here — the tolerance ``xtol``. `make` is a factory binding ``p``
once and returning the hot ``f(x, c)`` callable, which keeps the per-eval
signature minimal and lets implementations compile (e.g. ``numba.njit``) the
closure once per test function; the framework treats the returned callable as
opaque.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from ._recipes import ParamRecipe

# Hot signature of a materialized family: f(x, c) -> float, 64-bit in and out.
XCFun = Callable[[float, float], float]


def _always_valid(*_params: float) -> bool:
    """Accept any parameter tuple (default validity criterion)."""
    return True


# ==================================================================================================
#  Formula
# ==================================================================================================
@dataclass(frozen=True)
class Formula:
    """One hand-written formula: code plus the metadata to spawn candidate test functions.

    Attributes:
        number: Registry-wide formula number (grouping by type, e.g. 1xx polynomials).
        name: Short human-readable slug.
        make: Factory ``make(*p) -> f(x, c)`` binding a parameter tuple.
        bracket: ``bracket(*p) -> (a, b)``, the x-interval guaranteed to bracket a root.
        param_names: Names of the ``p`` tuple's positions, for display and slugs.
        recipes: Grid recipes that materialize candidate parameter tuples.
        is_param_tuple_valid: Up-front validity criterion for a parameter tuple.
    """

    number: int
    name: str
    make: Callable[..., XCFun]
    bracket: Callable[..., tuple[float, float]]
    param_names: tuple[str, ...] = ()
    recipes: tuple[ParamRecipe, ...] = ()
    is_param_tuple_valid: Callable[..., bool] = field(default=_always_valid)

    def __post_init__(self) -> None:
        """Validate that the formula number is positive."""
        if self.number <= 0:
            raise ValueError(f"Formula number must be > 0 (got {self.number}).")
