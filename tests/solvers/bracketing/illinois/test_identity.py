"""These tests assert the name and version of `Illinois`, and that its arithmetic is counted."""

from sunnbear.solvers import Illinois
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`Illinois` is named ``illinois``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Illinois().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Illinois.name, Illinois.version) == ("illinois", 1)
    assert result.flop_counts.total_count() > 0
