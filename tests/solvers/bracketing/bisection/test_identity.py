"""These tests assert the name and version of `Bisection`, and that its arithmetic is counted."""

from sunnbear.solvers import Bisection
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`Bisection` is named ``bisection``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Bisection().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert (Bisection.name, Bisection.version) == ("bisection", 1)
    assert result.flop_counts.total_count() > 0
