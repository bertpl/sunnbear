"""Real `Bisection` runs spend exactly `n_bisection_fevals` for an `xtol` at either bound of the range from
`compute_xtol_range`.

`max_fevals_for` returns the evaluation budget derived from that count.
"""

import math

import pytest

from sunnbear._core.benchmark.protocol.tolerances import (
    DEFAULT_N_BISECTION_FEVALS,
    MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND,
    XTOL_RANGE_MARGIN_SAFETY_FACTOR,
    compute_xtol_range,
    max_fevals_for,
)
from sunnbear.solvers import Bisection, SolveStatus


# ==================================================================================================
#  compute_xtol_range
# ==================================================================================================
@pytest.mark.parametrize(
    "a, b",
    [
        (1.0, 2.0),  # exact binary fractions
        (-0.3, 0.1),  # around 0
        (1.3, 1.4),
        # max(|a|, |b|) / (b - a) just below 1024, the largest ratio accepted at the default `n_bisection_fevals`
        (1022.7, 1023.7),
        (-1023.7, -1022.7),
    ],
)
@pytest.mark.parametrize("n_bisection_fevals", [3, 10, DEFAULT_N_BISECTION_FEVALS])
@pytest.mark.parametrize("bound", ["lower", "upper"])
def test_bisection_spends_exactly_n_bisection_fevals_at_both_bounds_of_the_xtol_range(a, b, n_bisection_fevals, bound):
    """Bisection spends exactly `n_bisection_fevals` at both bounds of the range, also on intervals whose bounds are not
    exact binary fractions and lie far from 0 for their width."""
    # --- arrange ----------------------
    xtol_min, xtol_max = compute_xtol_range(a=a, b=b, n_bisection_fevals=n_bisection_fevals)
    xtol = xtol_min if bound == "lower" else xtol_max
    root = a + (b - a) / math.pi

    def f(x: float) -> float:
        """Return -1 below `root` and 1 at and above `root`, so that no midpoint evaluates to 0, which would end the
        solve before it spends `n_bisection_fevals`."""
        if x >= root:
            return 1.0
        else:
            return -1.0

    # --- act --------------------------
    result = Bisection().solve(f, a, b, xtol=xtol, max_fevals=max_fevals_for(n_bisection_fevals=n_bisection_fevals))

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals == n_bisection_fevals


def test_the_xtol_range_lies_just_inside_its_exact_arithmetic_range_on_an_interval_around_0():
    """On [-1, 3], bisection spends exactly 5 evaluations in exact arithmetic for `xtol` in [0.25, 0.5), whose lower
    edge is the width 4 times `2^(1 - 5)`; the returned range lies a few float64 spacings inside each edge."""
    # --- act --------------------------
    xtol_min, xtol_max = compute_xtol_range(a=-1.0, b=3.0, n_bisection_fevals=5)

    # --- assert -----------------------
    assert 0.25 < xtol_min < xtol_max < 0.5
    assert (xtol_min, xtol_max) == pytest.approx((0.25, 0.5), rel=1e-14)


def test_the_margin_is_largest_and_below_one_half_at_the_largest_accepted_bound_to_width_ratio():
    """On [1023, 1024], whose ratio `max(|a|, |b|) / (b - a)` is the largest that the default `n_bisection_fevals`
    accepts, the margin in log2(xtol) is `XTOL_RANGE_MARGIN_SAFETY_FACTOR / (2*k*ln(2))`, with `k` the constant
    `MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND`, so the range is never empty."""
    # --- arrange ----------------------
    xtol_min_in_exact_arithmetic = 2.0 ** (1 - DEFAULT_N_BISECTION_FEVALS)
    margin_log2 = XTOL_RANGE_MARGIN_SAFETY_FACTOR / (
        2 * MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND * math.log(2.0)
    )

    # --- act --------------------------
    xtol_min, xtol_max = compute_xtol_range(a=1023.0, b=1024.0, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)

    # --- assert -----------------------
    assert margin_log2 < 0.5
    assert math.log2(xtol_min / xtol_min_in_exact_arithmetic) == pytest.approx(margin_log2, rel=1e-12)
    assert math.log2(xtol_max / xtol_min_in_exact_arithmetic) == pytest.approx(1 - margin_log2, rel=1e-12)


@pytest.mark.parametrize(
    "a, b, n_bisection_fevals, message",
    [
        (1.0, 1.0, 40, "a < b"),
        (2.0, 1.0, 40, "a < b"),
        (1.0, 2.0, 1, "at least 2"),
    ],
)
def test_compute_xtol_range_rejects_an_ill_ordered_interval_or_too_few_evaluations(a, b, n_bisection_fevals, message):
    """`compute_xtol_range` raises `ValueError` when `a >= b` or `n_bisection_fevals` is below 2."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        compute_xtol_range(a=a, b=b, n_bisection_fevals=n_bisection_fevals)


@pytest.mark.parametrize(
    "a, b, is_accepted",
    [
        (1023.0, 1024.0, True),  # max(|a|, |b|) = 1024 * (b - a): exactly at the limit
        (1024.0, 1025.0, False),  # max(|a|, |b|) = 1025 * (b - a): just beyond the limit
        (-1e6, 1e6, True),  # an interval that contains 0
    ],
)
def test_compute_xtol_range_rejects_an_interval_too_far_from_0_for_its_width(a, b, is_accepted):
    """With the default `n_bisection_fevals`, `compute_xtol_range` accepts an interval with
    `max(|a|, |b|) <= 1024 * (b - a)`, where 1024 =
    `2^(53 - DEFAULT_N_BISECTION_FEVALS) / MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND`, and raises
    `ValueError` beyond that."""
    # --- act / assert -----------------
    if is_accepted:
        compute_xtol_range(a=a, b=b, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
    else:
        with pytest.raises(ValueError, match="too far from 0"):
            compute_xtol_range(a=a, b=b, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)


# ==================================================================================================
#  max_fevals_for
# ==================================================================================================
def test_the_default_evaluation_budget_is_160_evaluations():
    """The default `n_bisection_fevals` gives a budget of 160 evaluations."""
    # --- act / assert -----------------
    assert max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS) == 160


def test_max_fevals_for_rejects_too_few_evaluations():
    """`max_fevals_for` raises `ValueError` when `n_bisection_fevals` is below 2."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="at least 2"):
        max_fevals_for(n_bisection_fevals=1)
