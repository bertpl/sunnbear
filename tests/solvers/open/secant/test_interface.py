"""These tests assert the name and version of `Secant`, and that its arithmetic is counted."""

from sunnbear.solvers import Secant
from tests.solvers.example_functions import cubic


def test_name_version_and_that_its_arithmetic_is_counted():
    """`Secant` is named ``secant``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Secant.name, Secant.version) == ("secant", 1)
    assert result.flop_counts.total_count() > 0
