"""`map_fevals_to_feature` maps evaluation counts onto [0, 1] on a log scale, for a feature vector's solvers block.

`map_feature_to_fevals` maps them back.

A correct solve takes at least 2 evaluations, 1 at each interval bound, and an incorrect one counts as `max_fevals`,
so every evaluation count of the block lies in [2, max_fevals]. `map_fevals_to_feature` maps that range onto [0, 1]
as ``log(n / 2) / log(max_fevals / 2)``; `map_feature_to_fevals` inverts it.
"""

import numpy as np
from numpy.typing import ArrayLike


def map_fevals_to_feature(n_fevals: ArrayLike, *, max_fevals: int) -> np.ndarray:
    """Return the feature value of each evaluation count in `n_fevals`, in [0, 1] for counts in [2, max_fevals]."""
    return np.log(np.asarray(n_fevals, dtype=np.float64) / 2) / np.log(max_fevals / 2)


def map_feature_to_fevals(feature_values: ArrayLike, *, max_fevals: int) -> np.ndarray:
    """Return the evaluation count of each value in `feature_values`, the inverse of `map_fevals_to_feature`."""
    return 2 * (max_fevals / 2) ** np.asarray(feature_values, dtype=np.float64)
