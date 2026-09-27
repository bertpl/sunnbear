"""The `xtol` band and the evaluation budget follow from bisection's evaluation count, as real `Bisection` runs confirm."""

import pytest

from sunnbear._core.benchmark.tolerances import N_BISECTION_FEVALS, max_fevals_for, xtol_range
from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.example_functions import cubic


# ==================================================================================================
#  xtol_range
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, 2.0), (0.0, 4.0), (1.3, 1.4)])  # Each interval holds the cubic's root.
@pytest.mark.parametrize("n_bisection_fevals", [3, 10, N_BISECTION_FEVALS])
@pytest.mark.parametrize(
    "edge, factor, n_fevals_offset",
    [
        ("lower", 1.01, 0),  # just inside the band
        ("upper", 0.99, 0),
        ("lower", 0.99, 1),  # just outside: 1 more step below the band, 1 fewer above it
        ("upper", 1.01, -1),
    ],
)
def test_bisection_takes_exactly_n_bisection_fevals_inside_the_band_only(
    a, b, n_bisection_fevals, edge, factor, n_fevals_offset
):
    """The 1 % margins around each edge absorb the rounding of the midpoints of a non-dyadic interval."""
    # --- arrange ----------------------
    xtol_min, xtol_max = xtol_range(a, b, n_bisection_fevals)
    xtol = factor * (xtol_min if edge == "lower" else xtol_max)

    # --- act --------------------------
    result = Bisection().solve(cubic, a, b, xtol=xtol, max_fevals=max_fevals_for(n_bisection_fevals))

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals == n_bisection_fevals + n_fevals_offset


def test_the_band_spans_a_factor_2_and_scales_with_the_interval_width():
    # --- act --------------------------
    band = xtol_range(-1.0, 3.0, 5)

    # --- assert -----------------------
    assert band == (0.25, 0.5)  # 4 · 2^(1 - 5)


@pytest.mark.parametrize(
    "a, b, n_bisection_fevals, message",
    [
        (1.0, 1.0, 40, "a < b"),
        (2.0, 1.0, 40, "a < b"),
        (1.0, 2.0, 1, "at least 2"),
    ],
)
def test_xtol_range_rejects_an_ill_ordered_interval_or_too_few_evaluations(a, b, n_bisection_fevals, message):
    with pytest.raises(ValueError, match=message):
        xtol_range(a, b, n_bisection_fevals)


# ==================================================================================================
#  max_fevals_for
# ==================================================================================================
def test_the_default_budget_is_160_evaluations():
    assert max_fevals_for(N_BISECTION_FEVALS) == 160


def test_max_fevals_for_rejects_too_few_evaluations():
    with pytest.raises(ValueError, match="at least 2"):
        max_fevals_for(1)
