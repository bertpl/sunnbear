"""These tests assert that `ModAB` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import ModAB, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic, ninth_power


@pytest.mark.parametrize(
    "f, a, b, root",
    [
        (cubic, 1.0, 2.0, CUBIC_ROOT),
        (decreasing_cubic, 1.0, 2.0, CUBIC_ROOT),
        (ninth_power, -1.0, 4.0, 0.0),
    ],
    ids=["cubic", "decreasing_cubic", "ninth_power"],
)
def test_a_function_converges_to_its_root(f, a, b, root):
    """On `cubic`, which increases, `decreasing_cubic`, which decreases, and `ninth_power` over ``[-1, 4]``, whose
    multiple root keeps the function from looking close enough to a straight line for `ModAB` to switch to
    Anderson-Björck mode, `ModAB` returns an x-value within ``xtol`` of the root."""
    # --- act --------------------------
    result = ModAB().solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
