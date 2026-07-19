import numpy as np
import pytest

from sunnbear.stats import gini_mean_difference, mean_pairwise_l1


# ==================================================================================================
#  gini_mean_difference
# ==================================================================================================
def test_gini_mean_difference_worked_example():
    # --- arrange ----------------------
    values = [1.0, 4.0, 9.0]  # pairwise |diffs|: 3 + 8 + 5 = 16 over 3 pairs

    # --- act / assert -----------------
    assert gini_mean_difference(values) == pytest.approx(16.0 / 3.0)


def test_gini_mean_difference_matches_brute_force():
    # --- arrange ----------------------
    rng = np.random.default_rng(11)
    values = rng.normal(size=50)
    brute = np.mean([abs(a - b) for i, a in enumerate(values) for b in values[i + 1 :]])

    # --- act / assert -----------------
    assert gini_mean_difference(values) == pytest.approx(float(brute))


def test_gini_mean_difference_order_invariant():
    assert gini_mean_difference([9.0, 1.0, 4.0]) == pytest.approx(gini_mean_difference([1.0, 4.0, 9.0]))


@pytest.mark.parametrize("values", [[], [1.0], [[1.0, 2.0], [3.0, 4.0]]])
def test_gini_mean_difference_rejects_invalid_input(values):
    with pytest.raises(ValueError):
        gini_mean_difference(values)


# ==================================================================================================
#  mean_pairwise_l1
# ==================================================================================================
def test_mean_pairwise_l1_matches_brute_force():
    # --- arrange ----------------------
    rng = np.random.default_rng(13)
    vectors = rng.normal(size=(40, 5))
    brute = np.mean([np.sum(np.abs(vectors[i] - vectors[j])) for i in range(40) for j in range(i + 1, 40)])

    # --- act / assert -----------------
    assert mean_pairwise_l1(vectors) == pytest.approx(float(brute))


def test_mean_pairwise_l1_decomposes_over_dimensions():
    # --- arrange ----------------------
    rng = np.random.default_rng(17)
    vectors = rng.normal(size=(30, 4))

    # --- act --------------------------
    total = mean_pairwise_l1(vectors)
    per_dimension = [gini_mean_difference(vectors[:, k]) for k in range(4)]

    # --- assert -----------------------
    assert total == pytest.approx(sum(per_dimension))


@pytest.mark.parametrize("vectors", [np.zeros((1, 3)), np.zeros(5), np.zeros((2, 2, 2))])
def test_mean_pairwise_l1_rejects_invalid_input(vectors):
    with pytest.raises(ValueError):
        mean_pairwise_l1(vectors)
