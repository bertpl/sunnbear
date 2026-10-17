"""A benchmark's tolerances and its evaluation budget all follow from 1 number, `n_bisection_fevals`.

`n_bisection_fevals` is the number of function evaluations that bisection spends on a solve, the 2 at
the interval bounds included.

The benchmark compares solvers by their function evaluations, so the evaluation budget `max_fevals` and
the `xtol` range are both derived from bisection's count. The `xtol` range is the set of `xtol` values on
which bisection spends exactly `n_bisection_fevals`.
"""

import math

from sunnbear._core.utils.floats import FLOAT64_EPS

# The shipped default of `n_bisection_fevals`.
DEFAULT_N_BISECTION_FEVALS = 40

# A solve's evaluation budget is this many times bisection's evaluation count.
MAX_FEVALS_FACTOR = 4

# `xtol_min` from `compute_xtol_range` must be at least this many times `FLOAT64_EPS * max(|a|, |b|)`, so that `xtol`
# spans at least this many float64 spacings at the interval bounds:
# - the interval can shrink to the shared stopping width of `2*xtol`;
# - the minimum step of `Brent`, `xtol + 2*FLOAT64_EPS*|b|`, stays below `2*xtol`, so that no step lands on the far
#   interval bound.
MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND = 8


def compute_xtol_range(*, a: float, b: float, n_bisection_fevals: int) -> tuple[float, float]:
    """Return the bounds `(xtol_min, 2·xtol_min)` of the `xtol` values on which bisection spends `n_bisection_fevals`.

    `Bisection` spends 1 evaluation per step and takes `ceil(log2((b - a) / (2·xtol)))` steps, so with the 2
    evaluations at the interval bounds it spends `ceil(log2((b - a) / (2·xtol))) + 2` evaluations in total.
    With `xtol_min = (b - a) · 2^(1 - n_bisection_fevals)`, that total equals `n_bisection_fevals` exactly when
    `xtol_min <= xtol < 2·xtol_min`, and no larger interval of `xtol` values has that property. Near either
    edge, rounding of the midpoints can shift the count by 1 when `a` and `b` are not exact binary fractions,
    so pick `xtol` well inside the range.

    `xtol_min` must be at least
    `MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND · FLOAT64_EPS · max(|a|, |b|)`, so that every solver can
    guarantee a result within `xtol_min` of a root.

    That minimum is met only when `max(|a|, |b|) <= (b - a) · 2^(53 - n_bisection_fevals) / k`, with `k` the constant
    `MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND`, so an interval far from 0 relative to its width is
    rejected; at the default `n_bisection_fevals`, every interval that contains 0 is accepted.

    Raises:
        ValueError: If any of these holds:
            - `a >= b`;
            - `n_bisection_fevals` is below 2 (bisection always evaluates both interval bounds);
            - `xtol_min` is below the minimum above.
    """
    if not a < b:
        raise ValueError(f"Interval must satisfy a < b (got a={a}, b={b}).")
    validate_n_bisection_fevals(n_bisection_fevals)
    xtol_min = math.ldexp(b - a, 1 - n_bisection_fevals)
    xtol_min_allowed = MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND * FLOAT64_EPS * max(abs(a), abs(b))
    if xtol_min < xtol_min_allowed:
        raise ValueError(
            f"The interval [{a}, {b}] lies too far from 0 for its width: its smallest xtol, {xtol_min:g}, is below "
            f"{MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND} · FLOAT64_EPS · max(|a|, |b|) = "
            f"{xtol_min_allowed:g}."
        )
    return xtol_min, 2.0 * xtol_min


def max_fevals_for(*, n_bisection_fevals: int) -> int:
    """Return a solve's evaluation budget: `MAX_FEVALS_FACTOR` times bisection's evaluation count.

    Raises:
        ValueError: If `n_bisection_fevals` is below 2 (bisection always evaluates both interval bounds).
    """
    validate_n_bisection_fevals(n_bisection_fevals)
    return MAX_FEVALS_FACTOR * n_bisection_fevals


def validate_n_bisection_fevals(n_bisection_fevals: int) -> None:
    """Raise `ValueError` if `n_bisection_fevals` is below 2: bisection always evaluates both interval bounds."""
    if n_bisection_fevals < 2:
        raise ValueError(f"n_bisection_fevals must be at least 2 (got {n_bisection_fevals}).")
