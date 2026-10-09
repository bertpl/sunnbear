"""These tests assert the name and version of `AndersonBjorck`, and that its arithmetic is counted."""

from sunnbear.solvers import AndersonBjorck
from tests.solvers.example_functions import cubic


def test_name_version_and_that_its_arithmetic_is_counted():
    """`AndersonBjorck` is named ``anderson_bjorck``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = AndersonBjorck().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (AndersonBjorck.name, AndersonBjorck.version) == ("anderson_bjorck", 1)
    assert result.flop_counts.total_count() > 0
