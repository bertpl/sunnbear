"""These tests assert that `Brent` takes the steps of Brent's procedure, and stops within ``xtol`` of a root."""

import pytest

from sunnbear.solvers import Bisection, Brent, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


def _ninth_power(x: float) -> float:
    """Return ``x^9``, whose root at 0 is a multiple root, on which interpolation converges slowly."""
    return x**9


# ==================================================================================================
#  The steps
# ==================================================================================================
def test_the_first_step_is_a_secant_step_from_the_bound_with_the_smaller_abs_f():
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step from 1,
    to 1 + 1/6."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic` in both interval orientations, `Brent` returns an evaluated point within ``xtol`` of the root."""
    # --- act --------------------------
    result = Brent().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_through_forced_bisections():
    """On ``x^9`` over ``[-1, 4]``, where interpolation converges slowly, `Brent` still converges within ``xtol``,
    with at most 3 times the evaluations of bisection."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    brent = Brent().solve(_ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)
    bisection = Bisection().solve(_ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert brent.status is SolveStatus.CONVERGED
    assert abs(brent.x) <= xtol
    assert brent.n_fevals <= 3 * bisection.n_fevals


def test_an_xtol_below_the_machine_precision_of_the_bounds_is_never_met():
    """Below ``6 * macheps * max(|a|, |b|)``, Brent's tolerance ``tol`` is negative, so the solve exhausts its
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
