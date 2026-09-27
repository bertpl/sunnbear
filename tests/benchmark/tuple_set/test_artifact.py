"""The `uv_tuples` artifact round-trips through its CSV file, and `uv_tuples(size)` returns the shipped sets."""

import numpy as np
import pytest

from sunnbear._core.artifacts import ArtifactError
from sunnbear._core.benchmark.tuple_set import UV_TUPLES_SIZES, UvTuples, UvTuplesDeclaration, uv_tuples


def test_the_csv_file_reads_back_every_value_exactly():
    """Every value written to the CSV file, behind the header `u,v`, reads back as the same float64."""
    # --- arrange ----------------------
    tuples = UvTuples(np.random.default_rng(7).random(5) * 0.9 + 0.05, [0.1, 0.2, 1 / 3, 0.5, 0.123456789012345678])

    # --- act --------------------------
    files = UvTuplesDeclaration.to_files(tuples)
    read_back = UvTuplesDeclaration.from_files(files)

    # --- assert -----------------------
    assert files["uv_tuples.csv"].startswith(b"u,v\n")
    assert read_back.u.tolist() == tuples.u.tolist()
    assert read_back.v.tolist() == tuples.v.tolist()


def test_a_csv_file_without_the_header_is_refused():
    """A CSV file that does not start with `u,v` raises an `ArtifactError`."""
    with pytest.raises(ArtifactError, match="starts with"):
        UvTuplesDeclaration.from_files({"uv_tuples.csv": b"x,y\n0.1,0.2\n"})


@pytest.mark.parametrize("size", UV_TUPLES_SIZES)
def test_uv_tuples_returns_a_prefix_of_the_shipped_set_that_meets_its_span_constraints(size):
    """Each size is the start of the full shipped set, and keeps every span within 1 of `size / N_SPANS`."""
    # --- act --------------------------
    tuples = uv_tuples(size)

    # --- assert -----------------------
    full = uv_tuples(max(UV_TUPLES_SIZES))
    assert tuples.size == size
    assert tuples.u.tolist() == full.u[:size].tolist()
    assert tuples.v.tolist() == full.v[:size].tolist()
    assert tuples.stats().max_span_count_deviation <= 1


def test_uv_tuples_rejects_an_unsupported_size():
    """A size that is not one of the shipped sizes raises a `ValueError` listing them."""
    with pytest.raises(ValueError, match=r"one of \[32, 64, 128, 256, 512, 1024\]"):
        uv_tuples(100)
