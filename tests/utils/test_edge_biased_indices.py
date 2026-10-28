"""`select_edge_biased_indices` selects symmetric indices whose gaps grow geometrically from both ends to the center."""

import numpy as np
import pytest

from sunnbear._core.utils.edge_biased_indices import select_edge_biased_indices


@pytest.mark.parametrize(
    "n_selected, n_total, indices",
    [
        # Every index: the ratio is 1.
        (4, 4, [0, 1, 2, 3]),
        # The gaps 1 and 2: the ratio is 2.
        (4, 5, [0, 1, 3, 4]),
        # The ratio is about 9.38.
        (8, 1024, [0, 1, 10, 98, 925, 1013, 1022, 1023]),
        # The ratio is about 2.37.
        (16, 1024, [0, 1, 3, 9, 22, 54, 128, 304, 719, 895, 969, 1001, 1014, 1020, 1022, 1023]),
    ],
)
def test_select_edge_biased_indices(n_selected, n_total, indices):
    """The indices are the rounded sums of geometric gaps whose next term is the gap between the 2 middle indices."""
    # --- act / assert -----------------
    assert select_edge_biased_indices(n_selected=n_selected, n_total=n_total).tolist() == indices


@pytest.mark.parametrize(
    "n_selected, n_total",
    [(4, 1024), (6, 7), (16, 256), (16, 4096), (32, 1024), (64, 1024), (1022, 1023), (1024, 1024)],
)
def test_select_edge_biased_indices_are_distinct_and_symmetric(n_selected, n_total):
    """The indices ascend strictly from 0 and 1, and index `i` is selected exactly when `n_total - 1 - i` is."""
    # --- act --------------------------
    indices = select_edge_biased_indices(n_selected=n_selected, n_total=n_total)

    # --- assert -----------------------
    assert indices.dtype == np.int64
    assert indices.size == n_selected
    assert indices[:2].tolist() == [0, 1]
    assert np.all(np.diff(indices) > 0)
    assert np.array_equal(indices, n_total - 1 - indices[::-1])


@pytest.mark.parametrize(
    "n_selected, n_total, match",
    [
        (5, 1024, "n_selected must be even"),
        (2, 1024, "n_selected must be even and at least 4"),
        (8, 6, "n_total must be at least n_selected"),
    ],
)
def test_select_edge_biased_indices_rejects_invalid_counts(n_selected, n_total, match):
    """An odd `n_selected`, one below 4, or an `n_total` below `n_selected` raises a `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=match):
        select_edge_biased_indices(n_selected=n_selected, n_total=n_total)
