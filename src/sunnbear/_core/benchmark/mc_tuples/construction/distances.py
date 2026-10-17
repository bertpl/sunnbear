"""max-div measures the distances between tuples cyclically: each axis is a circle on which 0 and 1 meet.

The distance between 2 values on an axis is the shorter of the 2 arcs between them, `min(d, 1 - d)` for a difference
`d`, so the unit square becomes a torus. A circle and a line leave different numbers of gaps:

- on a circle, the `k` values of a size leave `k` gaps, so the next size's `k` new values fit 1 per gap;
- on a line whose 2 ends are occupied, `k` values leave `k - 1` gaps, and 1 gap has to take 2 new values.

max-div calls each distance function through `DistanceMetric.custom`. numba compiles the functions, so they are
module-level.
"""

import numba
import numpy as np
from max_div.metrics import DistanceMetric


@numba.njit(fastmath={"reassoc", "contract"})
def cyclic_distance_along_axis(a: np.ndarray, b: np.ndarray, axis: int) -> float:
    """Return the distance between the tuples `a` and `b` along `axis`, on the circle of circumference 1."""
    difference = abs(float(a[axis]) - float(b[axis]))
    return min(difference, 1.0 - difference)


@numba.njit(fastmath={"reassoc", "contract"})
def cyclic_squared_l2_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the squared L2 distance between the tuples `a` and `b` on the torus, each axis measured on its circle."""
    total = 0.0
    for axis in range(a.shape[0]):
        difference = abs(float(a[axis]) - float(b[axis]))
        cyclic_difference = min(difference, 1.0 - difference)
        total += cyclic_difference * cyclic_difference
    return total


CYCLIC_U_DISTANCE_METRIC = DistanceMetric.custom(cyclic_distance_along_axis, label="cyclic u", params=(0,))
CYCLIC_V_DISTANCE_METRIC = DistanceMetric.custom(cyclic_distance_along_axis, label="cyclic v", params=(1,))
CYCLIC_SQUARED_L2_DISTANCE_METRIC = DistanceMetric.custom(cyclic_squared_l2_distance, label="cyclic squared L2")
