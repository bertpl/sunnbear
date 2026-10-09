"""These tests assert the name and version of `Brent`, and that its arithmetic is counted."""

from sunnbear.solvers import Brent
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`Brent` is named ``brent``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Brent.name, Brent.version) == ("brent", 1)
    assert result.flop_counts.total_count() > 0
