"""These tests assert that the individual steps of `RegulaFalsi` follow its algorithm."""

import pytest

from sunnbear.solvers import RegulaFalsi, SolveStatus


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The parametrization exercises both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    # --- act --------------------------
    result = RegulaFalsi().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    # The chord is the function, so the first iterate is the exact root and the stopping criterion holds immediately.
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)
