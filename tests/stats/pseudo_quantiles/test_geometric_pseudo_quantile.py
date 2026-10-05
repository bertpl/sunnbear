"""`gpq` computes the geometric pseudo-quantile, and `gpq_expression` gives the same value per group in polars."""

import numpy as np
import pytest

from sunnbear._core.stats.pseudo_quantiles import gpq_expression
from sunnbear.stats import gpq, owg

from .sample_values import VALUES_BY_GROUP, VALUES_WITH_A_ZERO, frame_of_values_by_group


# ==================================================================================================
#  gpq
# ==================================================================================================
def test_gpq_50_is_geomean():
    # --- arrange ----------------------
    values = [1.0, 2.0, 4.0, 8.0, 32.0]

    # --- act / assert -----------------
    assert gpq(values, 0.5) == pytest.approx(float(np.exp(np.mean(np.log(values)))))


@pytest.mark.parametrize(
    "q, p",
    [(0.10, -8.0), (0.25, -2.0), (1 / 3, -1.0), (0.5, 0.0), (2 / 3, 1.0), (0.75, 2.0), (0.90, 8.0)],
)
def test_gpq_calibration_reference_points(q, p):
    # --- arrange ----------------------
    values = [1.0, 3.0, 7.0, 20.0, 55.0, 148.0]

    # --- act / assert -----------------
    assert gpq(values, q) == pytest.approx(owg(values, p))


def test_gpq_monotonic_in_q():
    # --- arrange ----------------------
    rng = np.random.default_rng(7)
    values = rng.integers(4, 60, size=100).astype(float)
    q_ladder = [k / 10 for k in range(1, 10)]

    # --- act --------------------------
    results = [gpq(values, q) for q in q_ladder]

    # --- assert -----------------------
    assert results == sorted(results)


def test_gpq_antisymmetric_calibration():
    # --- arrange ----------------------
    values = [1.0, 4.0, 9.0, 25.0]

    # --- act / assert -----------------
    # p(1-q) = -p(q): gpq at mirrored levels equals owg at negated powers
    assert gpq(values, 0.25) == pytest.approx(owg(values, -2.0))
    assert gpq(values, 0.75) == pytest.approx(owg(values, 2.0))


@pytest.mark.parametrize(
    "values, q, expected",
    [
        ([4.0, 9.0, 1.0], 0.0, 1.0),
        ([4.0, 9.0, 1.0], 1.0, 9.0),
        (VALUES_WITH_A_ZERO, 0.0, 0.0),
        (VALUES_WITH_A_ZERO, 0.25, 0.0),
        (VALUES_WITH_A_ZERO, 0.5, 0.0),
        (VALUES_WITH_A_ZERO, 0.99, 0.0),
        (VALUES_WITH_A_ZERO, 1.0, 9.0),
    ],
)
def test_gpq_exact_results(values, q, expected):
    """The levels 0 and 1 give the exact extremes, and a zero makes the result 0 at every level below 1."""
    # --- act / assert -----------------
    assert gpq(values, q) == expected


@pytest.mark.parametrize("n", [1, 10, 1000])
@pytest.mark.parametrize("q, extreme", [(1e-12, np.min), (1e-7, np.min), (1.0 - 1e-7, np.max), (1.0 - 1e-12, np.max)])
def test_gpq_at_levels_close_to_0_or_1_gives_the_extreme(n, q, extreme):
    """At levels very close to 0 or 1, `gpq` gives the min or the max of the values."""
    # --- arrange ----------------------
    values = np.random.default_rng(n).uniform(1.0, 100.0, n)

    # --- act / assert -----------------
    assert gpq(values, q) == pytest.approx(extreme(values), rel=1e-12)


@pytest.mark.parametrize("q", [-0.5, 1.5, -1e-12, 1.0 + 1e-12, float("nan")])
def test_gpq_rejects_out_of_range_q(q):
    with pytest.raises(ValueError):
        gpq([1.0, 2.0], q)


# ==================================================================================================
#  Polars expression
# ==================================================================================================
@pytest.mark.parametrize("q", [0.0, 1e-12, 0.1, 0.25, 0.5, 0.75, 0.99, 1.0 - 1e-12, 1.0])
def test_gpq_expression_equals_gpq_per_group(q):
    """Per group, the expression gives the value of `gpq`, at the endpoint levels and with a zero too."""
    # --- act --------------------------
    results = frame_of_values_by_group().group_by("group").agg(gpq_expression("value", q).alias("gpq"))

    # --- assert -----------------------
    for group, result in results.iter_rows():
        assert result == pytest.approx(gpq(VALUES_BY_GROUP[group], q), rel=1e-12)


@pytest.mark.parametrize("q", [-0.5, 1.5, float("nan")])
def test_gpq_expression_refuses_out_of_range_q(q):
    """An out-of-range or NaN level raises `ValueError` when the expression is built."""
    # --- act / assert -----------------
    with pytest.raises(ValueError):
        gpq_expression("value", q)
