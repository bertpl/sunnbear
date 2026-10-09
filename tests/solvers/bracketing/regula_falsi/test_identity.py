"""These tests assert the name and version of `RegulaFalsi`, and that its arithmetic is counted."""

from sunnbear.solvers import RegulaFalsi
from tests.solvers.example_functions import cubic


def test_identity_and_that_its_arithmetic_is_counted():
    # --- act --------------------------
    result = RegulaFalsi().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (RegulaFalsi.name, RegulaFalsi.version) == ("regula_falsi", 1)
    assert result.flop_counts.total_count() > 0
