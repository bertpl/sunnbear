"""These tests assert that `Brent` takes the steps of Brent's procedure, and stops within ``xtol`` of a root."""

import pytest

from sunnbear.solvers import Bisection, Brent, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


# ==================================================================================================
#  The steps
# ==================================================================================================
def test_the_first_step_is_a_secant_step_from_the_bound_with_the_smaller_abs_f():
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step from 1 to
    1 + 1/6."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `Brent` returns an evaluated point within
    ``xtol`` of the root."""
    # --- act --------------------------
    result = Brent().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_within_3_times_the_evaluations_of_bisection():
    """On ``x^9`` over ``[-1, 4]``, where interpolation converges slowly, `Brent` still converges within ``xtol``,
    with at most 3 times the evaluations of bisection."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    brent_result = Brent().solve(lambda x: x**9, -1.0, 4.0, xtol=xtol, max_fevals=500)
    bisection_result = Bisection().solve(lambda x: x**9, -1.0, 4.0, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert brent_result.status is SolveStatus.CONVERGED
    assert abs(brent_result.x) <= xtol
    assert brent_result.n_fevals <= 3 * bisection_result.n_fevals


def test_an_xtol_that_makes_tol_negative_is_never_met():
    """An ``xtol`` of 1e-17 on ``[1, 2]`` makes Brent's tolerance ``tol`` negative, so the solve exhausts its
    budget."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Brent` is named ``brent``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Brent.name, Brent.version) == ("brent", 1)
    assert result.flop_counts.total_count() > 0
