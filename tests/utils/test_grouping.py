import numpy as np
import pytest

from sunnbear._core.utils.grouping import group_indices_by_id


@pytest.mark.parametrize(
    "ids, groups",
    [
        ([], []),
        ([7], [[0]]),
        ([3, 1, 3, 2, 1], [[1, 4], [3], [0, 2]]),
    ],
)
def test_group_indices_by_id(ids, groups):
    """Each group holds the ascending indices of 1 id, and the groups follow the ids in ascending order."""
    assert [group.tolist() for group in group_indices_by_id(np.array(ids, dtype=np.int64))] == groups
