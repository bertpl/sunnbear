"""These tests check `Brent` against `scipy.optimize.brentq` through `BrentScipyTwin`."""

import pytest

from sunnbear.solvers import Brent
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import BrentScipyTwin


@pytest.mark.parametrize("test_case", BrentScipyTwin.compared_test_cases(), ids=str)
def test_brent_agrees_with_scipy_brentq(test_case):
    """`Brent` evaluates the same x-values as SciPy's brentq, on every test case of `TWIN_TEST_CASES` that the twin does
    not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Brent(), BrentScipyTwin(), test_case)
