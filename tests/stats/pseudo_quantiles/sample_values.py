"""Sample values shared by the pseudo-quantile tests: a large set with a zero, and values per group."""

import numpy as np
import polars as pl

# The smallest rank weight of these values, (0.5 / 1024) ** p, rounds to 0.0 in float64 for every p above
# about 97.7, and gpq uses a p of about 98 at level 0.99; the tests check that a zero still gives 0, not NaN.
VALUES_WITH_A_ZERO = np.linspace(0.0, 9.0, 1024)

_RNG = np.random.default_rng(3)
VALUES_BY_GROUP = {
    "lognormal": _RNG.lognormal(3.0, 1.0, 500),
    "counts": _RNG.integers(2, 60, 300).astype(float),
    "single": np.array([7.0]),
    "with_a_zero": VALUES_WITH_A_ZERO,
}


def frame_of_values_by_group() -> pl.DataFrame:
    """Return a frame with 1 row per value of `VALUES_BY_GROUP`, and the group of each value in the column `group`."""
    return pl.DataFrame(
        {
            "group": [group for group, values in VALUES_BY_GROUP.items() for _ in values],
            "value": np.concatenate(list(VALUES_BY_GROUP.values())),
        }
    )
