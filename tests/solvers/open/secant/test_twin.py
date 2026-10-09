"""These tests check `Secant` against SciPy's secant method through `SecantScipyTwin`."""

import pytest

from sunnbear.solvers import Secant
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import SecantScipyTwin


@pytest.mark.parametrize("test_case", SecantScipyTwin.compared_test_cases(), ids=str)
def test_secant_agrees_with_scipy_newton(test_case):
    """`Secant` evaluates the same x-values as SciPy's secant method, on every test case of `TWIN_TEST_CASES` that the
    twin does not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Secant(), SecantScipyTwin(), test_case)
