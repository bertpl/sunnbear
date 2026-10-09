"""These tests assert the name and version of `Pegasus`, and that its arithmetic is counted."""

from sunnbear.solvers import Pegasus
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`Pegasus` is named ``pegasus``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Pegasus().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Pegasus.name, Pegasus.version) == ("pegasus", 1)
    assert result.flop_counts.total_count() > 0
