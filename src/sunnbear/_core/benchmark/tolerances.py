"""A benchmark's tolerances and its evaluation budget all follow from 1 number, `n_bisection_fevals`.

`n_bisection_fevals` is the number of function evaluations that bisection spends on a solve, the 2 at
the interval bounds included.

The benchmark compares solvers by their function evaluations, so the evaluation budget `max_fevals` and
the `xtol` band are both derived from bisection's count. The `xtol` band is the range of `xtol` values on
which bisection spends exactly `n_bisection_fevals`.
"""

import math

# The shipped default of `n_bisection_fevals`.
N_BISECTION_FEVALS = 40

# A solve's evaluation budget is this many times bisection's evaluation count.
MAX_FEVALS_FACTOR = 4


def compute_xtol_band(*, a: float, b: float, n_bisection_fevals: int) -> tuple[float, float]:
    """Return the bounds `(xtol_min, 2·xtol_min)` of the `xtol` values on which bisection spends `n_bisection_fevals`.

    `Bisection` spends 1 evaluation per step and takes `ceil(log2((b - a) / (2·xtol)))` steps, so with the 2
    evaluations at the interval bounds it spends `ceil(log2((b - a) / (2·xtol))) + 2` evaluations in total.
    With `xtol_min = (b - a) · 2^(1 - n_bisection_fevals)`, that total equals `n_bisection_fevals` exactly when
    `xtol_min <= xtol < 2·xtol_min`, and no larger interval of `xtol` values has that property. Near either
    edge, rounding of the midpoints can shift the count by 1 when `a` and `b` are not exact binary fractions,
    so pick `xtol` well inside the band.

    Raises:
        ValueError: If `a >= b`, or if `n_bisection_fevals` is below 2 (bisection always evaluates both
            interval bounds).
    """
    if not a < b:
        raise ValueError(f"Interval must satisfy a < b (got a={a}, b={b}).")
    _validate_n_bisection_fevals(n_bisection_fevals)
    xtol_min = math.ldexp(b - a, 1 - n_bisection_fevals)
    return xtol_min, 2.0 * xtol_min


def max_fevals_for(*, n_bisection_fevals: int) -> int:
    """Return a solve's evaluation budget: `MAX_FEVALS_FACTOR` times bisection's evaluation count.

    Raises:
        ValueError: If `n_bisection_fevals` is below 2 (bisection always evaluates both interval bounds).
    """
    _validate_n_bisection_fevals(n_bisection_fevals)
    return MAX_FEVALS_FACTOR * n_bisection_fevals


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _validate_n_bisection_fevals(n_bisection_fevals: int) -> None:
    """Raise `ValueError` if `n_bisection_fevals` is below 2: bisection always evaluates both interval bounds."""
    if n_bisection_fevals < 2:
        raise ValueError(f"n_bisection_fevals must be at least 2 (got {n_bisection_fevals}).")
