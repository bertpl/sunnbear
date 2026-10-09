"""These tests assert that every variant of `Ridders` reproduces the first iteration of the example in its paper."""

import math

import pytest

from sunnbear.solvers import Ridders, RiddersVariant


@pytest.mark.parametrize("variant", RiddersVariant)
def test_the_first_iteration_reproduces_the_example_of_the_paper(variant):
    """On the paper's example, ``x^3 - x - 5`` on ``[-1, 3]``, the first iterate is 1.9128..., and the next interval
    is ``[1, 1.9128...]``, whose midpoint is the next point evaluated."""
    # --- act --------------------------
    result = Ridders(variant=variant).solve(
        lambda x: x**3 - x - 5.0, -1.0, 3.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    (x1, f1), (x3, _), (x1_next, _) = result.history[2:5]
    assert (x1, f1) == (1.0, -5.0)
    assert x3 == 1.0 + 2.0 * 1.0 / math.sqrt(1.0 - 19.0 / -5.0)  # f1 / f0 = 1 and f2 / f0 = -19 / 5
    assert 1.9128 < x3 < 1.9129  # The paper prints the iterate as 1.9128..., truncated.
    assert x1_next == 0.5 * (1.0 + x3)
