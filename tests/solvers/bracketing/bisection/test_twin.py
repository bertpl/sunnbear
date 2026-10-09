"""These tests check `Bisection` against `scipy.optimize.bisect` through `BisectionScipyTwin`."""

import pytest

from sunnbear.solvers import Bisection
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import BisectionScipyTwin


@pytest.mark.parametrize("test_case", BisectionScipyTwin.comparable_test_cases(), ids=str)
def test_bisection_agrees_with_scipy_bisect(test_case):
    """`Bisection` evaluates the same points as SciPy's bisect, on every shared twin test case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Bisection(), BisectionScipyTwin(), test_case)
