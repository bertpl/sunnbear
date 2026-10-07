"""These tests check `Secant` against SciPy's secant method through `SecantScipyTwin`."""

import pytest

from sunnbear.solvers import Secant
from tests.solvers.example_functions import steep_exponential
from tests.solvers.open.secant.scipy_twin import SecantScipyTwin
from tests.solvers.twins import TWIN_TEST_CASES, TwinTestCase, assert_agrees_with_twin

# The agreement check compares converged solves only. With xtol = 1e-10, Secant leaves the interval on
# steep_exponential, so the test leaves that case out; test_solver.py covers it. With xtol = 1e-4, both solvers stop
# at the same point, far from the root, and the test compares them.
_CASE_LEAVING_THE_INTERVAL = TwinTestCase(steep_exponential, 0.0, 1.0, 1e-10)


@pytest.mark.parametrize(
    "test_case", [test_case for test_case in TWIN_TEST_CASES if test_case != _CASE_LEAVING_THE_INTERVAL], ids=str
)
def test_secant_agrees_with_scipy_newton(test_case):
    """`Secant` evaluates the same points as SciPy's secant method, on the shared twin test cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Secant(), SecantScipyTwin(), test_case)
