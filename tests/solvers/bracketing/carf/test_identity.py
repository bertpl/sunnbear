"""These tests assert the name and version of `CARF`, and that its arithmetic is counted."""

from sunnbear.solvers import CARF


def test_identity_and_that_its_power_steps_are_counted():
    """`CARF` is named ``carf``, at version 1, and the logarithms and power of its power steps are flop-counted."""
    # --- act --------------------------
    result = CARF().solve(lambda x: x**9, -1.0, 4.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert (CARF.name, CARF.version) == ("carf", 1)
    assert result.flop_counts.LOG > 0
    assert result.flop_counts.POW > 0
