"""The built-in series meet these checks:

- they name their suites `sb-<size>a`, `sb-<size>b` and `pub-<size>`;
- the a-series gives an alias to each of its sizes;
- `BUILT_IN_SERIES_BY_ID` finds every built-in series by its id.
"""

import pytest

from sunnbear._core.benchmark.suites.benchmark_suite import (
    BUILT_IN_SERIES,
    BUILT_IN_SERIES_BY_ID,
    PUB_SERIES,
    SB_A_SERIES,
    SB_B_SERIES,
)
from sunnbear._core.problems.core import ProblemId


@pytest.mark.parametrize(
    "series, size, name_expected, aliases_expected",
    [
        pytest.param(SB_A_SERIES, 1024, "sb-1024a", ("sb-large",), id="a_series"),
        pytest.param(SB_B_SERIES, 64, "sb-64b", (), id="b_series"),
        pytest.param(PUB_SERIES, 512, "pub-512", (), id="pub_series"),
    ],
)
def test_the_built_in_series_name_their_suites(series, size, name_expected, aliases_expected):
    """A suite of a built-in series carries the name and the aliases of its size."""
    # --- arrange ----------------------
    problem_ids = [ProblemId.from_string(f"f99.1[p={idx + 1}]") for idx in range(size)]

    # --- act --------------------------
    suite = series.create_suite(problem_ids)

    # --- assert -----------------------
    assert (suite.series_id, suite.name, suite.aliases) == (series.series_id, name_expected, aliases_expected)


def test_the_a_series_gives_an_alias_to_each_of_its_sizes():
    """Every size of the a-series has an entry in its `aliases_by_size`, so that every suite of the a-series has an
    alias."""
    # --- act / assert -----------------
    assert set(SB_A_SERIES.aliases_by_size) == set(SB_A_SERIES.sizes)


def test_the_lookup_by_series_id_finds_every_built_in_series():
    """`BUILT_IN_SERIES_BY_ID` holds every built-in series under its own id, in the order of `BUILT_IN_SERIES`, which
    also shows that no 2 built-in series share an id."""
    # --- act / assert -----------------
    assert list(BUILT_IN_SERIES_BY_ID.items()) == [(series.series_id, series) for series in BUILT_IN_SERIES]
