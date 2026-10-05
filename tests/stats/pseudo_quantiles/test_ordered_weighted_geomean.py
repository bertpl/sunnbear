"""`owg` computes the ordered weighted geometric mean, and `owg_expression` gives the same value per group in polars."""

import numpy as np
import pytest

from sunnbear._core.stats.pseudo_quantiles import owg_expression
from sunnbear.stats import owg

from .sample_values import VALUES_BY_GROUP, VALUES_WITH_A_ZERO, frame_of_values_by_group


# ==================================================================================================
#  owg
# ==================================================================================================
@pytest.mark.parametrize("values", [[1.0, 4.0, 9.0], [3.0], [5.0, 5.0, 5.0, 5.0], [1e-6, 1.0, 1e6]])
def test_owg_p_zero_is_geomean(values):
    # --- act --------------------------
    result = owg(values, p=0.0)

    # --- assert -----------------------
    assert result == pytest.approx(float(np.exp(np.mean(np.log(values)))))


@pytest.mark.parametrize("p, expected", [(200.0, 9.0), (-200.0, 1.0), (1e6, 9.0), (-1e6, 1.0)])
def test_owg_large_abs_p_approaches_extremes(p, expected):
    """At a very large |p|, `owg` gives the max or the min of the values."""
    # --- arrange ----------------------
    values = [1.0, 4.0, 9.0]

    # --- act --------------------------
    result = owg(values, p)

    # --- assert -----------------------
    assert result == pytest.approx(expected, rel=1e-3)


def test_owg_monotonic_in_p():
    # --- arrange ----------------------
    values = [2.0, 3.0, 5.0, 8.0, 13.0]
    p_ladder = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]

    # --- act --------------------------
    results = [owg(values, p) for p in p_ladder]

    # --- assert -----------------------
    assert results == sorted(results)
    assert all(min(values) < r < max(values) for r in results)


def test_owg_order_invariant():
    # --- arrange ----------------------
    values = [9.0, 1.0, 4.0]
    shuffled = [4.0, 9.0, 1.0]

    # --- act / assert -----------------
    assert owg(values, 1.5) == pytest.approx(owg(shuffled, 1.5))


@pytest.mark.parametrize(
    "values, p, expected",
    [
        ([4.0, 9.0, 1.0], np.inf, 9.0),
        ([4.0, 9.0, 1.0], -np.inf, 1.0),
        (VALUES_WITH_A_ZERO, -3.0, 0.0),
        (VALUES_WITH_A_ZERO, 0.0, 0.0),
        (VALUES_WITH_A_ZERO, 98.0, 0.0),
        (VALUES_WITH_A_ZERO, np.inf, 9.0),
        (VALUES_WITH_A_ZERO, -np.inf, 0.0),
    ],
)
def test_owg_exact_results(values, p, expected):
    """Infinite powers give the exact extremes, and a zero makes the result 0 for every finite p."""
    # --- act / assert -----------------
    assert owg(values, p) == expected


@pytest.mark.parametrize("values", [[], [1.0, -2.0], [0.0, -1e-300]])
def test_owg_rejects_invalid_values(values):
    with pytest.raises(ValueError):
        owg(values, 1.0)


# ==================================================================================================
#  Polars expression
# ==================================================================================================
@pytest.mark.parametrize("p", [-np.inf, -1e6, -3.0, 0.0, 1.5, 1e6, np.inf])
def test_owg_expression_equals_owg_per_group(p):
    """Per group, the expression gives the value of `owg` at infinite and very large powers, and with a zero too."""
    # --- act --------------------------
    results = frame_of_values_by_group().group_by("group").agg(owg_expression("value", p).alias("owg"))

    # --- assert -----------------------
    for group, result in results.iter_rows():
        assert result == pytest.approx(owg(VALUES_BY_GROUP[group], p), rel=1e-12)
