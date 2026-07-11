import numpy as np
import pytest

from sunnbear.stats import gpq, owg


# ==================================================================================================
#  owg
# ==================================================================================================
@pytest.mark.parametrize("values", [[1.0, 4.0, 9.0], [3.0], [5.0, 5.0, 5.0, 5.0], [1e-6, 1.0, 1e6]])
def test_owg_p_zero_is_geomean(values):
    # --- act --------------------------
    result = owg(values, p=0.0)

    # --- assert -----------------------
    assert result == pytest.approx(float(np.exp(np.mean(np.log(values)))))


@pytest.mark.parametrize("p, expected", [(200.0, 9.0), (-200.0, 1.0)])
def test_owg_large_abs_p_approaches_extremes(p, expected):
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


@pytest.mark.parametrize("values", [[], [1.0, -2.0], [0.0, 1.0]])
def test_owg_rejects_invalid_values(values):
    with pytest.raises(ValueError):
        owg(values, 1.0)


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


@pytest.mark.parametrize("q", [0.0, 1.0, -0.5, 1.5])
def test_gpq_rejects_out_of_range_q(q):
    with pytest.raises(ValueError):
        gpq([1.0, 2.0], q)
