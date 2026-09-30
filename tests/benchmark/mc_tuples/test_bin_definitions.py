"""`MCTuplesBinDefinitions` cuts each axis into ⌊√size⌋ bins, with bounds that every size can meet."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesBinDefinitions, MCTuplesSize

# Each entry holds a shipped size, its number of bins per axis, and its smallest and largest allowed count per bin.
_SHIPPED_SIZE_BINS = [
    (MCTuplesSize.SIZE_32, 5, 5, 7),
    (MCTuplesSize.SIZE_64, 8, 7, 9),
    (MCTuplesSize.SIZE_128, 11, 11, 13),
    (MCTuplesSize.SIZE_256, 16, 15, 17),
    (MCTuplesSize.SIZE_512, 22, 22, 24),
    (MCTuplesSize.SIZE_1024, 32, 31, 33),
]


def test_the_expected_bins_cover_every_shipped_size():
    """`_SHIPPED_SIZE_BINS` names every member of `MCTuplesSize`, so a new size cannot go untested."""
    assert {size for size, *_ in _SHIPPED_SIZE_BINS} == set(MCTuplesSize)


@pytest.mark.parametrize("size, n_bins_per_axis, min_count_per_bin, max_count_per_bin", _SHIPPED_SIZE_BINS)
def test_the_shipped_sizes_have_sqrt_size_bins_with_bounds_around_the_rounded_count(
    size, n_bins_per_axis, min_count_per_bin, max_count_per_bin
):
    """Each shipped size has ⌊√size⌋ bins per axis, each allowing round(size / n_bins_per_axis) ± 1 tuples."""
    # --- act --------------------------
    bin_definitions = MCTuplesBinDefinitions(size=size)

    # --- assert -----------------------
    assert (bin_definitions.n_bins_per_axis, bin_definitions.min_count_per_bin, bin_definitions.max_count_per_bin) == (
        n_bins_per_axis,
        min_count_per_bin,
        max_count_per_bin,
    )


def test_the_bounds_can_be_met_by_every_size():
    """For sizes 2 to 4096, the bins' lower bounds sum to at most the size, and their upper bounds to at least it."""
    # --- act / assert -----------------
    for size in range(2, 4097):
        bin_definitions = MCTuplesBinDefinitions(size=size)
        n_bins_per_axis = bin_definitions.n_bins_per_axis
        assert (
            n_bins_per_axis * bin_definitions.min_count_per_bin
            <= size
            <= n_bins_per_axis * bin_definitions.max_count_per_bin
        )


def test_bin_indices_and_counts_cut_the_axis_into_equal_bins():
    """With 3 bins (sizes 9 to 15), a value in [i/3, (i+1)/3) is in bin i, and a value just below 1 in the last."""
    # --- arrange ----------------------
    bin_definitions = MCTuplesBinDefinitions(size=9)
    values = np.array([0.01, 0.34, 0.5, 0.67, 0.999999])

    # --- act / assert -----------------
    assert bin_definitions.bin_indices(values).tolist() == [0, 1, 1, 2, 2]
    assert bin_definitions.bin_counts(values) == (1, 2, 2)


def test_a_size_below_2_is_refused():
    """A tuple set holds at least 2 tuples, so a size of 1 raises `ValueError`."""
    with pytest.raises(ValueError, match="at least 2 tuples"):
        MCTuplesBinDefinitions(size=1)
