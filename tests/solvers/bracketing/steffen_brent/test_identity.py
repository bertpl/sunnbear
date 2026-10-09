"""These tests assert the identity of `SteffenBrent`, and that its arithmetic is counted."""

from sunnbear.solvers import SteffenBrent
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`SteffenBrent` is named ``steffen_brent``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = SteffenBrent().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (SteffenBrent.name, SteffenBrent.version) == ("steffen_brent", 1)
    assert result.flop_counts.total_count() > 0
