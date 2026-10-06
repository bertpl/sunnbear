"""These tests check `Ridders` against `scipy.optimize.ridder` through `RiddersScipyTwin`."""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant
from tests.solvers.bracketing.ridders.scipy_twin import RiddersScipyTwin
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize("test_case", TWIN_TEST_CASES, ids=str)
def test_ridders_agrees_with_scipy_ridder(test_case, variant):
    """`Ridders` evaluates the same points as SciPy's ridder, on every shared twin test case, in every variant."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Ridders(variant=variant), RiddersScipyTwin(variant=variant), test_case)
