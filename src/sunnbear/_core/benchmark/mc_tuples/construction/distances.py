"""The distance functions give max-div the cyclic distance between 2 base tuples, each standing for its 4 tuples.

Each axis is a circle on which 0 and 1 meet: the distance between 2 values on an axis is the shorter of the 2 arcs
between them, `min(d, 1 - d)` for a difference `d`, so the unit square becomes a torus. A circle and a line leave
different numbers of gaps:

- on a circle, the `k` values of a size leave `k` gaps, so the next size's `k` new values fit 1 per gap;
- on a line whose 2 ends are occupied, `k` values leave `k - 1` gaps, and 1 gap has to take 2 new values.

A candidate of the max-div problem is a base tuple, which stands for its 4 tuples (`rotations`).

A rotation keeps every cyclic distance, so the shortest distance between the 4 tuples of base tuple p and the 4 tuples
of base tuple q is the shortest distance from p to the 4 tuples of q; each of the 4 tuples of p has the same
nearest-neighbor distance.

A tuple's nearest neighbor can also be 1 of its rotational siblings, the other 3 tuples of its own base tuple. To count
these neighbors, every problem holds the dummy rotational sibling tuple at index 0: a vector with u < 0, which stands
for no real tuple and which every selection includes.

The distance from the dummy rotational sibling tuple to a base tuple is that base tuple's distance to its nearest
rotational sibling. max-div calls a distance function with the vector of the lower index first, so the dummy rotational
sibling tuple is always the first vector.

Along an axis, the 4 tuples of a base tuple hold 4 values, its u and v and their mirrors 1 - u and 1 - v, but max-div
gives each candidate only 1 nearest-neighbor distance.

One metric serves both axes: it takes the shortest distance between a value of 1 base tuple and a value or mirror of
the other. The first base tuple's mirrors need no separate check, because mirroring both values keeps their cyclic
distance.

A base tuple's nearest-neighbor distance along an axis is then the smaller of the nearest-neighbor distances of its u
and its v, and this distance is the same along u and along v.

numba compiles the distance functions that max-div calls through `DistanceMetric.custom`, so they are module-level.
"""

import numba
import numpy as np
from max_div.metrics import DistanceMetric

# The dummy rotational sibling tuple lies outside the unit square, so that a distance function recognizes it by its
# u < 0.
DUMMY_ROTATIONAL_SIBLING_TUPLE = np.array([-1.0, -1.0])


@numba.njit(fastmath={"reassoc", "contract"})
def _cyclic_distance(a: float, b: float) -> float:
    """Return the distance between `a` and `b` on the circle of circumference 1."""
    difference = abs(a - b)
    return min(difference, 1.0 - difference)


@numba.njit(fastmath={"reassoc", "contract"})
def _cyclic_squared_l2_distance(a_u: float, a_v: float, b_u: float, b_v: float) -> float:
    """Return the squared L2 distance between the tuples (`a_u`, `a_v`) and (`b_u`, `b_v`) on the torus."""
    du = _cyclic_distance(a_u, b_u)
    dv = _cyclic_distance(a_v, b_v)
    return du * du + dv * dv


@numba.njit(fastmath={"reassoc", "contract"})
def _cyclic_distance_to_value_or_mirror(a: float, b: float) -> float:
    """Return the distance on the circle from `a` to the nearer of `b` and its mirror `1 - b`."""
    return min(_cyclic_distance(a, b), _cyclic_distance(a, 1.0 - b))


@numba.njit(fastmath={"reassoc", "contract"})
def base_tuple_squared_l2_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the smallest squared cyclic L2 distance between base tuple `a` and the 4 tuples of base tuple `b`.

    With the dummy rotational sibling tuple as `a`, return the squared distance from `b` to the nearer of its rotations
    by 90 and by 180 degrees; its rotation by 270 degrees lies as far from it as its rotation by 90 degrees.
    """
    b_u, b_v = float(b[0]), float(b[1])
    if a[0] < 0.0:
        return min(
            _cyclic_squared_l2_distance(b_u, b_v, 1.0 - b_v, b_u),
            _cyclic_squared_l2_distance(b_u, b_v, 1.0 - b_u, 1.0 - b_v),
        )
    else:
        a_u, a_v = float(a[0]), float(a[1])
        return min(
            _cyclic_squared_l2_distance(a_u, a_v, b_u, b_v),
            _cyclic_squared_l2_distance(a_u, a_v, 1.0 - b_v, b_u),
            _cyclic_squared_l2_distance(a_u, a_v, 1.0 - b_u, 1.0 - b_v),
            _cyclic_squared_l2_distance(a_u, a_v, b_v, 1.0 - b_u),
        )


@numba.njit(fastmath={"reassoc", "contract"})
def base_tuple_value_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the smallest cyclic distance between a value of base tuple `a` and a value or mirror of base tuple `b`.

    With the dummy rotational sibling tuple as `a`, return the smallest of 3 distances: from the u of `b` to its v or to
    1 - v, from u to 1 - u, and from v to 1 - v.
    """
    b_u, b_v = float(b[0]), float(b[1])
    if a[0] < 0.0:
        return min(
            _cyclic_distance_to_value_or_mirror(b_u, b_v),
            _cyclic_distance(b_u, 1.0 - b_u),
            _cyclic_distance(b_v, 1.0 - b_v),
        )
    else:
        a_u, a_v = float(a[0]), float(a[1])
        return min(
            _cyclic_distance_to_value_or_mirror(a_u, b_u),
            _cyclic_distance_to_value_or_mirror(a_u, b_v),
            _cyclic_distance_to_value_or_mirror(a_v, b_u),
            _cyclic_distance_to_value_or_mirror(a_v, b_v),
        )


BASE_TUPLE_SQUARED_L2_DISTANCE_METRIC = DistanceMetric.custom(
    base_tuple_squared_l2_distance, label="base-tuple cyclic squared L2"
)
BASE_TUPLE_VALUE_DISTANCE_METRIC = DistanceMetric.custom(base_tuple_value_distance, label="base-tuple cyclic value")
