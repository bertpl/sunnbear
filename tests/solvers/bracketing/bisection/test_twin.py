"""These tests check `Bisection` against `scipy.optimize.bisect` through `BisectionScipyTwin`."""

import pytest

from sunnbear.solvers import Bisection
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import BisectionScipyTwin


@pytest.mark.parametrize("test_case", BisectionScipyTwin.compared_test_cases(), ids=str)
def test_bisection_agrees_with_scipy_bisect(test_case):
    """`Bisection` evaluates the same x-values as SciPy's bisect, on every test case of `TWIN_TEST_CASES` that the twin
    does not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Bisection(), BisectionScipyTwin(), test_case)
