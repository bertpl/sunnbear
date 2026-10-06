"""These tests check `Bisection` against `scipy.optimize.bisect` through `BisectionScipyTwin`."""

import pytest
from counted_float import FlopCounts

from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.bracketing.bisection.scipy_twin import BisectionScipyTwin
from tests.solvers.example_functions import cubic
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


# ==================================================================================================
#  The twin itself
# ==================================================================================================
def test_the_twin_counts_evaluations_but_no_solver_arithmetic():
    """The twin's evaluations are counted, but SciPy's arithmetic on plain floats is not."""
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
@pytest.mark.parametrize("test_case", TWIN_TEST_CASES, ids=str)
def test_bisection_agrees_with_scipy_bisect(test_case):
    """`Bisection` evaluates the same points as SciPy's bisect, on every shared twin test case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Bisection(), BisectionScipyTwin(), test_case)
