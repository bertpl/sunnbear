"""These tests assert that `Bisection` converges within ``xtol`` with the exact evaluation count."""

import math

import pytest

from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # Exercises both interval orientations.
@pytest.mark.parametrize("a, b, xtol", [(1.0, 2.0, 1e-3), (0.0, 4.0, 1e-8), (1.3, 1.4, 1e-12)])
def test_converges_within_xtol_with_the_exact_evaluation_count(f, a, b, xtol):
    # --- arrange ----------------------
    n_steps_expected = math.ceil(math.log2((b - a) / (2.0 * xtol)))
    n_fevals_expected = n_steps_expected + 2

    # --- act --------------------------
    result = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= xtol
    assert result.n_fevals == n_fevals_expected
