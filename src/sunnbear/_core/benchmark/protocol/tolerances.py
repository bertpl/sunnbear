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

# Every `xtol` in the range from `compute_xtol_range` must be at least this many times
# `FLOAT64_EPS * max(|a|, |b|)`, so that `xtol` spans at least this many float64 spacings at the interval bounds:
# - the interval can shrink to the shared stopping width of `2*xtol`;
# - the minimum step of `Brent`, `xtol + 2*FLOAT64_EPS*|b|`, stays below `2*xtol`, so that no step lands on the
#   interval bound `c` on the other side of the root from `b`.
MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND = 8

# `compute_xtol_range` keeps a margin from each edge of the `xtol` range that exact arithmetic gives, as a distance in
# log2(xtol); the margin is this many times the largest change of log2(xtol) that the rounding of bisection's
# midpoints can cause.
XTOL_RANGE_MARGIN_SAFETY_FACTOR = 2.0


def compute_xtol_range(*, a: float, b: float, n_bisection_fevals: int) -> tuple[float, float]:
    """Return the bounds `(xtol_min, xtol_max)` of the `xtol` values on which bisection spends `n_bisection_fevals`.

    `Bisection` spends 1 evaluation per step and takes `ceil(log2((b - a) / (2*xtol)))` steps, so with the 2
    evaluations at the interval bounds it spends `ceil(log2((b - a) / (2*xtol))) + 2` evaluations in total. In exact
    arithmetic, that total equals `n_bisection_fevals` exactly when
    `xtol_min_in_exact_arithmetic <= xtol < 2*xtol_min_in_exact_arithmetic`, with
    `xtol_min_in_exact_arithmetic = (b - a) * 2^(1 - n_bisection_fevals)`.

    In float64, the count can shift by 1 near either edge of that range: the stopping test `width <= 2*xtol` compares
    2 equal values at `xtol_min_in_exact_arithmetic` and 2 nearly equal values just below
    `2*xtol_min_in_exact_arithmetic`, and the computed interval bounds are rounded midpoints.

    So the returned range keeps a margin `margin_log2` from each edge, measured in log2(xtol), that grows with the
    bound-to-width ratio `max(|a|, |b|) / (b - a)` and with `n_bisection_fevals`: its bounds are
    `xtol_min_in_exact_arithmetic * 2^margin_log2` and `xtol_min_in_exact_arithmetic * 2^(1 - margin_log2)`.

    `xtol_min_in_exact_arithmetic` must be at least
    `MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND * FLOAT64_EPS * max(|a|, |b|)`, so that every solver can
    guarantee a result within `xtol` of a root.

    That minimum is met only when `max(|a|, |b|) <= (b - a) * 2^(53 - n_bisection_fevals) / k`, with `k` the constant
    `MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND`, so an interval far from 0 relative to its width is
    rejected; at the default `n_bisection_fevals`, every interval that contains 0 is accepted.

    On an accepted interval, `margin_log2` is at most `XTOL_RANGE_MARGIN_SAFETY_FACTOR / (2*k*ln(2))`, which is below
    1/2, so the lower bound `margin_log2` of `log2(xtol / xtol_min_in_exact_arithmetic)` stays below its upper bound
    `1 - margin_log2` and the range is never empty.

    Raises:
        ValueError: If any of these holds:
            - `a >= b`;
            - `n_bisection_fevals` is below 2 (bisection always evaluates both interval bounds);
            - `xtol_min_in_exact_arithmetic` is below the minimum above.
    """
    if not a < b:
        raise ValueError(f"Interval must satisfy a < b (got a={a}, b={b}).")
    validate_n_bisection_fevals(n_bisection_fevals)
    xtol_min_in_exact_arithmetic = math.ldexp(b - a, 1 - n_bisection_fevals)
    xtol_min_allowed = MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND * FLOAT64_EPS * max(abs(a), abs(b))
    if xtol_min_in_exact_arithmetic < xtol_min_allowed:
        raise ValueError(
            f"The interval [{a}, {b}] lies too far from 0 for its width: its smallest xtol in exact arithmetic, "
            f"{xtol_min_in_exact_arithmetic:g}, is below {MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND} * "
            f"FLOAT64_EPS * max(|a|, |b|) = {xtol_min_allowed:g}."
        )

    # The margin `margin_log2`, in log2(xtol), is `XTOL_RANGE_MARGIN_SAFETY_FACTOR` times the bound on rounding's
    # effect:
    # - after `n_bisection_fevals - 2` halvings, the computed width is off by at most about
    #   `FLOAT64_EPS * max(|a|, |b|)`, which is `FLOAT64_EPS * bound_to_width_ratio * 2^(n_bisection_fevals - 2)`
    #   relative to `2*xtol`;
    # - a relative change of `xtol`, divided by `ln(2)`, is the change of log2(xtol).
    bound_to_width_ratio = max(abs(a), abs(b)) / (b - a)
    margin_log2 = (
        XTOL_RANGE_MARGIN_SAFETY_FACTOR
        * FLOAT64_EPS
        * bound_to_width_ratio
        * math.ldexp(1.0, n_bisection_fevals - 2)
        / math.log(2.0)
    )
    return xtol_min_in_exact_arithmetic * 2.0**margin_log2, xtol_min_in_exact_arithmetic * 2.0 ** (1.0 - margin_log2)


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
