"""These tests check `Chandrupatla` against `scipy.optimize.elementwise.find_root` through `ChandrupatlaScipyTwin`."""

import pytest

from sunnbear.solvers import Chandrupatla
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import ChandrupatlaScipyTwin


@pytest.mark.parametrize("test_case", ChandrupatlaScipyTwin.compared_test_cases(), ids=str)
def test_chandrupatla_agrees_with_scipy_find_root(test_case):
    """`Chandrupatla` evaluates the same x-values as SciPy's find_root, on every test case of `TWIN_TEST_CASES` that the
    twin does not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Chandrupatla(), ChandrupatlaScipyTwin(), test_case)
