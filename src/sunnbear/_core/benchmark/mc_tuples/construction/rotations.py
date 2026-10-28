"""Each size holds every base tuple with its 3 rotations around (0.5, 0.5).

The rotation by 90 degrees maps a tuple (u, v) to (1 - v, u), so the 4 tuples of a base tuple (u, v) are (u, v),
(1 - v, u), (1 - u, 1 - v) and (v, 1 - u). Each base tuple lies in [0, 0.5]^2, which holds exactly 1 of the 4 tuples.

Every size's u values and v values are then the same set, the values u, v, 1 - u and 1 - v of its base tuples, and the
values of each axis are symmetric around 0.5, so every size's means are 0.5.

No 2 tuples share a fine lane on either axis if and only if the u values and v values of all base tuples lie in
distinct fine lanes of [0, 0.5], the lower fine lanes.

On each axis, the values in [0, 0.5) are the base tuples' u and v values, and those in (0.5, 1) are their mirrors,
1 - u and 1 - v.

`MCTuplesSizeResult` builds a size's tuples from its base tuples.
"""

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES

# The base tuples' u values and v values lie in the lower fine lanes, the fine lanes of [0, 0.5];
# `N_LOWER_FINE_LANES` counts them.
N_LOWER_FINE_LANES = N_FINE_LANES // 2
