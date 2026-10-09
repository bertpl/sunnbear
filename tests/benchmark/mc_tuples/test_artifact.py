"""The `mc_tuples` artifact round-trips through its CSV file, and `load_mc_tuples(size)` returns the shipped sets."""

import numpy as np
import pytest

from sunnbear._core.artifacts import ArtifactError
from sunnbear._core.benchmark.mc_tuples import (
    N_FINE_LANES,
    MCTuples,
    MCTuplesDeclaration,
    MCTuplesSize,
    fine_lanes_of,
    load_mc_tuples,
)


def test_the_csv_file_reads_back_every_value_exactly():
    """Every value written to the CSV file, behind the header `u,v`, reads back as the same float64."""
    # --- arrange ----------------------
    tuples = MCTuples(np.random.default_rng(7).random(5) * 0.9 + 0.05, [0.1, 0.2, 1 / 3, 0.5, 0.123456789012345678])

    # --- act --------------------------
    files = MCTuplesDeclaration.to_files(tuples)
    read_back = MCTuplesDeclaration.from_files(files)

    # --- assert -----------------------
    assert files["mc_tuples.csv"].startswith(b"u,v\n")
    assert read_back.u.tolist() == tuples.u.tolist()
    assert read_back.v.tolist() == tuples.v.tolist()


def test_a_csv_file_without_the_header_is_refused():
    """A CSV file that does not start with `u,v` raises an `ArtifactError`."""
    with pytest.raises(ArtifactError, match="starts with"):
        MCTuplesDeclaration.from_files({"mc_tuples.csv": b"x,y\n0.1,0.2\n"})


@pytest.mark.parametrize("size", MCTuplesSize)
def test_load_mc_tuples_returns_a_prefix_of_the_shipped_set(size):
    """Each size is the start of the full shipped set."""
    # --- act --------------------------
    tuples = load_mc_tuples(size)

    # --- assert -----------------------
    full = load_mc_tuples(max(MCTuplesSize))
    assert tuples.size == size
    assert tuples.u.tolist() == full.u[:size].tolist()
    assert tuples.v.tolist() == full.v[:size].tolist()


@pytest.mark.parametrize("size", MCTuplesSize)
def test_each_shipped_size_has_means_of_0_5_and_at_most_1_tuple_per_fine_lane(size):
    """Each shipped size's mean u and mean v are 0.5, and no 2 of its tuples share a fine lane along u or along v."""
    # --- act --------------------------
    tuples = load_mc_tuples(size)

    # --- assert -----------------------
    assert tuples.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)
    for values in (tuples.u, tuples.v):
        assert np.bincount(fine_lanes_of(values)).max() == 1


def test_the_largest_shipped_size_holds_exactly_1_tuple_per_fine_lane():
    """The largest size fills every fine lane along u and along v with exactly 1 tuple."""
    # --- act --------------------------
    tuples = load_mc_tuples(max(MCTuplesSize))

    # --- assert -----------------------
    for values in (tuples.u, tuples.v):
        assert np.bincount(fine_lanes_of(values), minlength=N_FINE_LANES).tolist() == [1] * N_FINE_LANES


def test_load_mc_tuples_rejects_an_unsupported_size():
    """A size that is not one of the shipped sizes raises a `ValueError` listing them."""
    with pytest.raises(ValueError, match=r"one of \[32, 64, 128, 256, 512, 1024\]"):
        load_mc_tuples(100)
