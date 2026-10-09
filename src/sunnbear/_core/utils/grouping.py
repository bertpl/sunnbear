"""This module groups the positions of an array of integer ids by id."""

import numpy as np


def group_indices_by_id(ids: np.ndarray) -> list[np.ndarray]:
    """Return the indices of `ids`, grouped by id in ascending order; an empty list when `ids` is empty."""
    if ids.size == 0:
        return []
    else:
        order = np.argsort(ids, kind="stable")
        return np.split(order, np.flatnonzero(np.diff(ids[order])) + 1)
