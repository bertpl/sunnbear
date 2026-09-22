"""These tests check `Bisection` against `scipy.optimize.bisect` through `BisectionScipyTwin`."""

import pytest
from counted_float import FlopCounts

from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.bracketing.bisection.scipy_twin import BisectionScipyTwin
from tests.solvers.example_functions import cubic, decreasing_cubic, quintic

PROBLEMS = [(cubic, 1.0, 2.0), (quintic, 0.0, 1.0), (decreasing_cubic, 1.0, 2.0)]


# ==================================================================================================
#  The twin itself
# ==================================================================================================
def test_the_twin_counts_evaluations_but_no_solver_arithmetic():
    # --- act --------------------------
    result = BisectionScipyTwin().solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals > 2  # The count includes the 2 bound evaluations plus SciPy's own.
    # SciPy runs on plain floats, so only the framework's own checks and bookkeeping are counted.
    assert result.flop_counts == FlopCounts(COMP=4, ADD=1, MUL=1)


# ==================================================================================================
#  Agreement
# ==================================================================================================
@pytest.mark.parametrize("f, a, b", PROBLEMS)
@pytest.mark.parametrize("xtol", [1e-4, 1e-8])
def test_bisection_agrees_with_scipy_bisect(f, a, b, xtol):
    # --- act --------------------------
    ours = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)
    twin = BisectionScipyTwin().solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert ours.status is twin.status is SolveStatus.CONVERGED
    assert abs(ours.x - twin.x) <= xtol
    # SciPy stops on a slightly different width rule, so its own call count is ours within 1. It also re-evaluates
    # both bounds, and the twin's count includes both.
    assert abs((twin.n_fevals - 2) - ours.n_fevals) <= 1
