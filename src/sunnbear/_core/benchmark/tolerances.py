"""A benchmark's tolerances and its evaluation budget all follow from 1 number, `n_bisection_fevals`.

`n_bisection_fevals` is the number of function evaluations that bisection spends on a solve, the 2 at
the interval bounds included. Function evaluations are what the benchmark compares across solvers, so
both the evaluation budget `max_fevals` and the `xtol` band, meaning the range of `xtol` values on which
bisection spends exactly `n_bisection_fevals`, are derived from bisection's count.
"""

import math

# The shipped default of `n_bisection_fevals`, counting the 2 evaluations at the interval bounds.
N_BISECTION_FEVALS = 40

# A solve's evaluation budget is this many times bisection's evaluation count.
MAX_FEVALS_FACTOR = 4


def xtol_band(a: float, b: float, n_bisection_fevals: int) -> tuple[float, float]:
    """Return the bounds `(xtol_min, 2·xtol_min)` of the `xtol` values on which bisection takes exactly `n_bisection_fevals`.

    `Bisection` performs `ceil(log2((b - a) / (2·xtol)))` steps plus the 2 evaluations at the interval
    bounds. With `xtol_min = (b - a) · 2^(1 - n_bisection_fevals)`, that count equals `n_bisection_fevals`
    exactly when `xtol_min <= xtol < 2·xtol_min`, and no larger interval of `xtol` values has that property.

    Raises:
        ValueError: If `a >= b`, or if `n_bisection_fevals` is below 2 (bisection always evaluates both
            interval bounds).
    """
    if not a < b:
        raise ValueError(f"Interval must satisfy a < b (got a={a}, b={b}).")
    _check_n_bisection_fevals(n_bisection_fevals)
    xtol_min = math.ldexp(b - a, 1 - n_bisection_fevals)
    return xtol_min, 2.0 * xtol_min


def max_fevals_for(n_bisection_fevals: int) -> int:
    """Return a solve's evaluation budget: `MAX_FEVALS_FACTOR` times bisection's evaluation count.

    Raises:
        ValueError: If `n_bisection_fevals` is below 2 (bisection always evaluates both interval bounds).
    """
    _check_n_bisection_fevals(n_bisection_fevals)
    return MAX_FEVALS_FACTOR * n_bisection_fevals


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _check_n_bisection_fevals(n_bisection_fevals: int) -> None:
    """Raise `ValueError` if `n_bisection_fevals` is below 2: bisection always evaluates both interval bounds."""
    if n_bisection_fevals < 2:
        raise ValueError(f"n_bisection_fevals must be at least 2 (got {n_bisection_fevals}).")
