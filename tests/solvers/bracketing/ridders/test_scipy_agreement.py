"""These tests check `Ridders` against `scipy.optimize.ridder` through `RiddersScipyTwin`."""

import pytest

from sunnbear.solvers import Ridders
from tests.solvers.bracketing.ridders.scipy_twin import RiddersScipyTwin
from tests.solvers.twins import TWIN_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("stopping_criterion", ["original", "corrected"])
@pytest.mark.parametrize("case", TWIN_CASES, ids=str)
def test_ridders_agrees_with_scipy_ridder(case, stopping_criterion):
    """`Ridders` evaluates the same points as SciPy's ridder, on every shared twin case, under both stopping
    criteria."""
    # --- act / assert -----------------
    assert_agrees_with_twin(
        Ridders(stopping_criterion=stopping_criterion), RiddersScipyTwin(stopping_criterion=stopping_criterion), case
    )
