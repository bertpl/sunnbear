"""These tests assert that a solve of either variant of `Brent` ends at an x-value where the function is exactly 0, and
that neither variant meets the shared stopping criterion when ``xtol`` lies below the float spacing near the root."""

import pytest

from sunnbear.solvers import Brent, BrentVariant, SolveStatus
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize("variant", BrentVariant)
def test_an_exact_zero_ends_the_solve_at_that_point(variant):
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = Brent(variant=variant).solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize("variant", BrentVariant)
def test_an_xtol_below_the_float_spacing_near_the_root_is_never_met(variant):
    """An ``xtol`` of 1e-17 on ``[1, 2]`` lies below the float spacing near the root of `cubic`, about 2.2e-16, so the
    interval never gets as narrow as ``2*xtol``.

    Once the step is lengthened to Brent's tolerance ``tol``, it rounds onto the far interval bound ``c``, and the solve
    evaluates that x-value again and again until its budget is exhausted.
    """
    # --- act --------------------------
    result = Brent(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert len(set(result.evaluated_x_values[-10:])) == 1
