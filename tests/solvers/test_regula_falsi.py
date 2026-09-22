"""These tests assert `RegulaFalsi` on both sides of its known weakness: it converges on a chord, stalls on a curve."""

import pytest

from sunnbear.solvers import RegulaFalsi, SolveStatus


def _cubic(x: float) -> float:
    return x**3 - x - 1.0  # Has 1 real root, near 1.3247; convex on [1, 2], so the upper bound is retained.


ROOT = 1.324717957244746


# ==================================================================================================
#  Convergence and the stall
# ==================================================================================================
@pytest.mark.parametrize("f", [lambda x: x - 0.3, lambda x: 0.3 - x])  # Exercises both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    # --- act --------------------------
    result = RegulaFalsi().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    # The chord is the function, so the first iterate is the exact root and the zero-value criterion stops the loop.
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_a_convex_function_stalls_on_the_retained_bound_and_exhausts_the_budget():
    # --- act --------------------------
    result = RegulaFalsi().solve(_cubic, 1.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    # The iterates converge to the root, but the upper bound never moves, so the width criterion never holds.
    x_last, _ = result.history[-1]
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 60
    assert abs(x_last - ROOT) <= 1e-9
    assert result.x == 0.5 * (x_last + 2.0)  # The last interval's midpoint; the retained bound is 2.


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    # --- act --------------------------
    result = RegulaFalsi().solve(_cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (RegulaFalsi.name, RegulaFalsi.version) == ("regula_falsi", 1)
    assert result.flop_counts.total_count() > 0
