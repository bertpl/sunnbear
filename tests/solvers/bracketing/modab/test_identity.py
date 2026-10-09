"""These tests assert the name and version of `ModAB`, and that its arithmetic is counted."""

from sunnbear.solvers import ModAB
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`ModAB` is named ``modab``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = ModAB().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (ModAB.name, ModAB.version) == ("modab", 1)
    assert result.flop_counts.total_count() > 0
