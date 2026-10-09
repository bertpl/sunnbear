"""These tests assert the identity of `Chandrupatla`, and that its arithmetic is counted."""

from sunnbear.solvers import Chandrupatla
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    """`Chandrupatla` has name ``chandrupatla`` and version 1, and its flop count includes its square roots."""
    # --- act --------------------------
    result = Chandrupatla().solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=40)

    # --- assert -----------------------
    assert (Chandrupatla.name, Chandrupatla.version) == ("chandrupatla", 1)
    assert result.flop_counts.SQRT > 0
