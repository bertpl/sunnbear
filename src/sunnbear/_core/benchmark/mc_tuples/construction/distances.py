"""max-div measures the distance between 2 base tuples through their 4 tuples each, cyclically.

Each axis is a circle on which 0 and 1 meet: the distance between 2 values on an axis is the shorter of the 2 arcs
between them, `min(d, 1 - d)` for a difference `d`, so the unit square becomes a torus. A circle and a line leave
different numbers of gaps:

- on a circle, the `k` values of a size leave `k` gaps, so the next size's `k` new values fit 1 per gap;
- on a line whose 2 ends are occupied, `k` values leave `k - 1` gaps, and 1 gap has to take 2 new values.

A candidate of the max-div problem is a base tuple, which stands for its 4 tuples (`rotations`). A rotation keeps every
cyclic distance, so the shortest distance between the 4 tuples of base tuple p and the 4 tuples of base tuple q is the
shortest distance from p to the 4 tuples of q; the 4 tuples of p share their nearest-neighbor distance.

A tuple's nearest neighbor can also be 1 of the other 3 tuples of its own base tuple. The placeholder, a vector with
u < 0 at index 0 of every problem, which every selection holds, accounts for these: its distance to a base tuple is that
base tuple's distance to the nearest of its own other 3 tuples. max-div calls a distance function with the vector of the
lower index first, so the placeholder is always the first vector.

Along an axis, max-div gives each candidate 1 nearest-neighbor distance, but a base tuple holds 2 values on each axis,
its u and its v, with their mirrors 1 - u and 1 - v. The metric along the axes, 1 for both axes, takes the shortest
distance between a value of 1 base tuple and a value or mirror of the other, so a base tuple's separation is the smaller
of its 2 values' separations among all values of the axis; the separations along u and along v are the same values.

numba compiles the distance functions that max-div calls through `DistanceMetric.custom`, so they are module-level.
"""

import numba
import numpy as np
from max_div.metrics import DistanceMetric

# The placeholder's vector, outside the unit square, so that a distance function recognizes it by its u < 0.
PLACEHOLDER_TUPLE_ARRAY = np.array([[-1.0, -1.0]])


@numba.njit(fastmath={"reassoc", "contract"})
def _cyclic_difference(a: float, b: float) -> float:
    """Return the distance between `a` and `b` on the circle of circumference 1."""
    difference = abs(a - b)
    return min(difference, 1.0 - difference)


@numba.njit(fastmath={"reassoc", "contract"})
def _cyclic_squared_l2(a_u: float, a_v: float, b_u: float, b_v: float) -> float:
    """Return the squared L2 distance between the tuples (`a_u`, `a_v`) and (`b_u`, `b_v`) on the torus."""
    du = _cyclic_difference(a_u, b_u)
    dv = _cyclic_difference(a_v, b_v)
    return du * du + dv * dv


@numba.njit(fastmath={"reassoc", "contract"})
def _folded_difference(a: float, b: float) -> float:
    """Return the distance on the circle from `a` to the nearer of `b` and its mirror `1 - b`."""
    return min(_cyclic_difference(a, b), _cyclic_difference(a, 1.0 - b))


@numba.njit(fastmath={"reassoc", "contract"})
def rotational_squared_l2_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the smallest squared cyclic L2 distance between base tuple `a` and the 4 tuples of base tuple `b`.

    With the placeholder as `a`, return the squared distance from `b` to the nearer of its rotations by 90 and by 180
    degrees; its rotation by 270 degrees lies as far from it as its rotation by 90 degrees.
    """
    b_u, b_v = float(b[0]), float(b[1])
    if a[0] < 0.0:
        return min(_cyclic_squared_l2(b_u, b_v, 1.0 - b_v, b_u), _cyclic_squared_l2(b_u, b_v, 1.0 - b_u, 1.0 - b_v))
    else:
        a_u, a_v = float(a[0]), float(a[1])
        return min(
            _cyclic_squared_l2(a_u, a_v, b_u, b_v),
            _cyclic_squared_l2(a_u, a_v, 1.0 - b_v, b_u),
            _cyclic_squared_l2(a_u, a_v, 1.0 - b_u, 1.0 - b_v),
            _cyclic_squared_l2(a_u, a_v, b_v, 1.0 - b_u),
        )


@numba.njit(fastmath={"reassoc", "contract"})
def rotational_axis_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the smallest cyclic distance between a value of base tuple `a` and a value or mirror of base tuple `b`.

    With the placeholder as `a`, return the smallest distance between a value of `b` and its other value, that value's
    mirror, or its own mirror.
    """
    b_u, b_v = float(b[0]), float(b[1])
    if a[0] < 0.0:
        return min(_folded_difference(b_u, b_v), _cyclic_difference(b_u, 1.0 - b_u), _cyclic_difference(b_v, 1.0 - b_v))
    else:
        a_u, a_v = float(a[0]), float(a[1])
        return min(
            _folded_difference(a_u, b_u),
            _folded_difference(a_u, b_v),
            _folded_difference(a_v, b_u),
            _folded_difference(a_v, b_v),
        )


ROTATIONAL_SQUARED_L2_DISTANCE_METRIC = DistanceMetric.custom(
    rotational_squared_l2_distance, label="rotational cyclic squared L2"
)
ROTATIONAL_AXIS_DISTANCE_METRIC = DistanceMetric.custom(rotational_axis_distance, label="rotational cyclic axes")
