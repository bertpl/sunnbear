"""The cyclic distances measure each axis as a circle on which 0 and 1 meet, and the unit square as a torus."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples.construction.distances import (
    cyclic_distance_along_axis,
    cyclic_squared_l2_distance,
)


@pytest.mark.parametrize(
    "a, b, axis, expected",
    [
        ([0.05, 0.4], [0.95, 0.7], 0, 0.1),  # the shorter arc runs across 0 and 1
        ([0.05, 0.4], [0.95, 0.7], 1, 0.3),  # the shorter arc is the direct one
        ([0.25, 0.0], [0.75, 0.0], 0, 0.5),  # both arcs have the same length
    ],
)
def test_the_distance_along_an_axis_is_the_shorter_arc_between_the_2_values(a, b, axis, expected):
    """The distance along an axis is `min(d, 1 - d)` for the difference `d` of the 2 values on that axis."""
    # --- act --------------------------
    distance = cyclic_distance_along_axis(np.array(a), np.array(b), axis)

    # --- assert -----------------------
    assert distance == pytest.approx(expected)


def test_the_squared_l2_distance_adds_the_squares_of_the_shorter_arcs_of_both_axes():
    """The squared L2 distance of (0.05, 0.4) and (0.95, 0.7) is 0.1^2 + 0.3^2, not the linear 0.9^2 + 0.3^2."""
    # --- act --------------------------
    distance = cyclic_squared_l2_distance(np.array([0.05, 0.4]), np.array([0.95, 0.7]))

    # --- assert -----------------------
    assert distance == pytest.approx(0.1**2 + 0.3**2)
