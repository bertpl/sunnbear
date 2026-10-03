"""The `mc_tuples` artifact round-trips through its CSV file, and `load_mc_tuples(size)` returns the shipped sets."""

import numpy as np
import pytest

from sunnbear._core.artifacts import ArtifactError
from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesDeclaration, MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid


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
def test_load_mc_tuples_returns_a_prefix_of_the_shipped_set_with_1_tuple_per_lane(size):
    """Each size is the start of the full shipped set, with exactly 1 tuple in each of its lanes along u and along v."""
    # --- act --------------------------
    tuples = load_mc_tuples(size)

    # --- assert -----------------------
    full = load_mc_tuples(max(MCTuplesSize))
    size_below = None if size == min(MCTuplesSize) else load_mc_tuples(size // 2)
    assert tuples.size == size
    assert tuples.u.tolist() == full.u[:size].tolist()
    assert tuples.v.tolist() == full.v[:size].tolist()
    assert LaneGrid.for_size(size, size_below).is_one_per_lane(tuples)


def test_load_mc_tuples_rejects_an_unsupported_size():
    """A size that is not one of the shipped sizes raises a `ValueError` listing them."""
    with pytest.raises(ValueError, match=r"one of \[32, 64, 128, 256, 512, 1024\]"):
        load_mc_tuples(100)
