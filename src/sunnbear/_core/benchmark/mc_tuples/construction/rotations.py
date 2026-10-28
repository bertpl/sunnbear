"""Each size holds every base tuple with its 3 rotations around (0.5, 0.5).

The rotation by 90 degrees maps a tuple (u, v) to (1 - v, u), so the 4 tuples of a base tuple (u, v) are (u, v),
(1 - v, u), (1 - u, 1 - v) and (v, 1 - u). Each base tuple lies in [0, 0.5]^2, which holds exactly 1 of the 4 tuples.

Every size's u values and v values are then the same set, the values u, v, 1 - u and 1 - v of its base tuples, and the
values of each axis are symmetric around 0.5, so every size's means are 0.5. The 4 tuples are built from these 4
values, never by rotating a tuple 3 times: in float64, `1.0 - (1.0 - v)` is not always `v`.

No 2 tuples share a fine lane on either axis if and only if the u values and v values of all base tuples lie in
distinct fine lanes of [0, 0.5], the lower fine lanes: the values in [0, 0.5) of each axis are the base tuples' u and v
values, and those in (0.5, 1) their mirrors, 1 - u and 1 - v.
"""

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES

# The base tuples' u values and v values lie in the lower fine lanes, the fine lanes of [0, 0.5];
# `N_LOWER_FINE_LANES` counts them.
N_LOWER_FINE_LANES = N_FINE_LANES // 2


def tuple_array_of(base_tuple_array: np.ndarray) -> np.ndarray:
    """Return each base tuple's 4 tuples as consecutive rows, the base tuple first.

    The 3 rows after a base tuple are its rotations by 90, 180 and 270 degrees.
    """
    u, v = base_tuple_array[:, 0], base_tuple_array[:, 1]
    mirrored_u, mirrored_v = 1.0 - u, 1.0 - v
    rotations = [
        np.column_stack([u, v]),
        np.column_stack([mirrored_v, u]),
        np.column_stack([mirrored_u, mirrored_v]),
        np.column_stack([v, mirrored_u]),
    ]
    return np.stack(rotations, axis=1).reshape(-1, 2)
