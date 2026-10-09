"""These tests assert that `CARF` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import CARF, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize(
    "f, a, b, root",
    [
        (cubic, 1.0, 2.0, CUBIC_ROOT),
        (decreasing_cubic, 1.0, 2.0, CUBIC_ROOT),
        (lambda x: x**9, -1.0, 4.0, 0.0),
    ],
    ids=["cubic", "decreasing_cubic", "multiple_root"],
)
def test_a_function_converges_to_its_root(f, a, b, root):
    """On `cubic`, which increases, `decreasing_cubic`, which decreases, and ``x^9`` over ``[-1, 4]``, where the
    multiple root makes `CARF` take power steps, `CARF` returns an x-value within ``xtol`` of the root."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
