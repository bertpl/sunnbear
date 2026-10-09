"""These tests assert the name and version of `CARF`, and that the logarithms and powers of its power steps are
counted."""

from sunnbear.solvers import CARF
from tests.solvers.example_functions import ninth_power


def test_name_version_and_that_its_arithmetic_is_counted():
    """`CARF` is named ``carf``, at version 1, and the logarithms and power of its power steps are flop-counted."""
    # --- act --------------------------
    result = CARF().solve(ninth_power, -1.0, 4.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert (CARF.name, CARF.version) == ("carf", 1)
    assert result.flop_counts.LOG > 0
    assert result.flop_counts.POW > 0
