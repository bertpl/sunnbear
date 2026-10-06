"""These tests check `Secant` against SciPy's secant method through `SecantScipyTwin`."""

import pytest

from sunnbear.solvers import Secant
from tests.solvers.example_functions import steep_exponential
from tests.solvers.open.secant.scipy_twin import SecantScipyTwin
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


# The agreement check compares converged solves only. On steep_exponential, Secant leaves the interval at
# xtol = 1e-10, so the test leaves that function out; test_solver.py covers it.
@pytest.mark.parametrize(
    "test_case", [test_case for test_case in TWIN_TEST_CASES if test_case.f is not steep_exponential], ids=str
)
def test_secant_agrees_with_scipy_newton(test_case):
    """`Secant` evaluates the same points as SciPy's secant method, on the shared twin test cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Secant(), SecantScipyTwin(), test_case)
