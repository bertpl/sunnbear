"""Each size holds every base tuple with its 3 rotations around (0.5, 0.5); `tuple_array_of` builds them.

The rotation by 90 degrees maps a tuple (u, v) to (1 - v, u), so the 4 tuples of a base tuple (u, v) are (u, v),
(1 - v, u), (1 - u, 1 - v) and (v, 1 - u). Each base tuple lies in [0, 0.5]^2, which holds exactly 1 of the 4 tuples.

Every size's u values and v values are then the same set, the values u, v, 1 - u and 1 - v of its base tuples, and the
values of each axis are symmetric around 0.5, so every size's means are 0.5.

On each axis, the values in [0, 0.5) are the base tuples' u and v values, and those in (0.5, 1) are their mirrors,
1 - u and 1 - v.

The rotations map a size's LHS lanes onto LHS lanes and its tiles onto tiles (`MCTuplesSize`), and of the 4 tiles that
they map onto each other, exactly 1 lies in [0, 0.5]^2. So a size holds exactly 1 tuple in each LHS lane and each tile
if and only if:

- its base tuples' u values and v values lie in distinct LHS lanes of [0, 0.5], the lower-half LHS lanes, and fill
  all of them;
- its base tuples lie in distinct tiles of [0, 0.5]^2 and fill all of them.
"""

import numpy as np


def tuple_array_of(base_tuple_array: np.ndarray) -> np.ndarray:
    """Return each base tuple's 4 tuples as consecutive rows, the base tuple first.

    The 3 rows after a base tuple are its rotations by 90, 180 and 270 degrees.
    """
    u, v = base_tuple_array[:, 0], base_tuple_array[:, 1]
    # The 4 tuples are built from these 4 values, never by rotating a tuple 3 times: in float64,
    # `1.0 - (1.0 - v)` is not always `v`.
    mirrored_u, mirrored_v = 1.0 - u, 1.0 - v
    rotations = [
        np.column_stack([u, v]),
        np.column_stack([mirrored_v, u]),
        np.column_stack([mirrored_u, mirrored_v]),
        np.column_stack([v, mirrored_u]),
    ]
    return np.stack(rotations, axis=1).reshape(-1, 2)
