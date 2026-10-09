"""These tests assert that the individual steps of `CARF` follow its algorithm."""

import pytest

from sunnbear.solvers import CARF
from tests.solvers.example_functions import cubic, steep_exponential


@pytest.mark.parametrize(
    "f, a, b, first_x",
    [(cubic, 1.0, 2.0, 1.0 + 1.0 / 6.0), (steep_exponential, 0.0, 1.0, 0.1)],
    ids=["chord_zero_inside", "chord_zero_clipped"],
)
def test_the_first_x_value_is_the_chord_zero_clipped_into_the_middle_80_percent(f, a, b, first_x):
    """The first x-value is the chord's zero, kept when it lies in the middle 80 % of the interval and clipped to its
    edge otherwise."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(first_x, abs=1e-15)
