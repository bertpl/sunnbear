"""The distances between base tuples, the placeholder included, give each base tuple its 4 tuples' separations."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples.construction.distances import (
    PLACEHOLDER_TUPLE_ARRAY,
    rotational_axis_distance,
    rotational_squared_l2_distance,
)
from sunnbear._core.benchmark.mc_tuples.construction.rotations import N_LOWER_FINE_LANES, tuple_array_of


def _random_base_tuple_array(n: int, seed: int) -> np.ndarray:
    """Return `n` random base tuples whose u values and v values lie in 2n distinct lower fine lanes."""
    rng = np.random.default_rng(seed)
    lanes = rng.permutation(N_LOWER_FINE_LANES)[: 2 * n].reshape(2, n)
    return ((lanes + rng.random((2, n))) / (2 * N_LOWER_FINE_LANES)).T


def _cyclic_separations(tuple_array: np.ndarray, axes: list[int]) -> np.ndarray:
    """Return each tuple's cyclic L2 distance to its nearest other tuple, over the given axes."""
    differences = np.abs(tuple_array[:, None, axes] - tuple_array[None, :, axes])
    distances = np.sqrt((np.minimum(differences, 1.0 - differences) ** 2).sum(axis=2))
    np.fill_diagonal(distances, np.inf)
    return distances.min(axis=1)


def _separations_through_candidates(base_tuple_array: np.ndarray, distance_function) -> np.ndarray:
    """Return each base tuple's smallest distance to another candidate, the placeholder included, as max-div sees it."""
    vectors = np.vstack([PLACEHOLDER_TUPLE_ARRAY, base_tuple_array]).astype(np.float32)
    n = vectors.shape[0]
    distances = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(i + 1, n):
            distances[i, j] = distances[j, i] = distance_function(vectors[i], vectors[j])
    return distances[1:].min(axis=1)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_l2_separation_of_each_base_tuple_is_that_of_its_4_tuples(seed):
    """Each base tuple's squared L2 separation among the candidates is the squared separation of its 4 tuples."""
    # --- arrange ----------------------
    base_tuple_array = _random_base_tuple_array(16, seed)

    # --- act --------------------------
    separations = _separations_through_candidates(base_tuple_array, rotational_squared_l2_distance)

    # --- assert -----------------------
    expected = _cyclic_separations(tuple_array_of(base_tuple_array), [0, 1]).reshape(-1, 4) ** 2
    assert np.allclose(expected, expected[:, :1])
    assert separations == pytest.approx(expected[:, 0], abs=1e-7)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_axis_separation_of_each_base_tuple_is_the_smaller_of_its_2_values(seed):
    """Each base tuple's separation along the axes is the smallest separation along u among its 4 tuples."""
    # --- arrange ----------------------
    base_tuple_array = _random_base_tuple_array(16, seed)

    # --- act --------------------------
    separations = _separations_through_candidates(base_tuple_array, rotational_axis_distance)

    # --- assert -----------------------
    tuple_array = tuple_array_of(base_tuple_array)
    separations_u, separations_v = _cyclic_separations(tuple_array, [0]), _cyclic_separations(tuple_array, [1])
    assert np.sort(separations_u) == pytest.approx(np.sort(separations_v))
    assert separations == pytest.approx(separations_u.reshape(-1, 4).min(axis=1), abs=1e-7)


def test_the_placeholder_sees_a_base_tuple_near_the_center_close_to_its_own_rotations():
    """A base tuple at distance d from (0.5, 0.5) lies d * sqrt(2) from its rotation by 90 degrees."""
    # --- arrange ----------------------
    base_tuple = np.array([0.5 - 0.003, 0.5 - 0.004], dtype=np.float32)

    # --- act --------------------------
    distance = rotational_squared_l2_distance(PLACEHOLDER_TUPLE_ARRAY[0].astype(np.float32), base_tuple)

    # --- assert -----------------------
    assert distance == pytest.approx(2 * (0.003**2 + 0.004**2), abs=1e-7)
