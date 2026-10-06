"""These tests check `Chandrupatla` against `scipy.optimize.elementwise.find_root` through `ChandrupatlaScipyTwin`."""

import pytest

from sunnbear.solvers import Chandrupatla
from tests.solvers.bracketing.chandrupatla.scipy_twin import ChandrupatlaScipyTwin
from tests.solvers.twins import TWIN_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("case", TWIN_CASES, ids=str)
def test_chandrupatla_agrees_with_scipy_find_root(case):
    """`Chandrupatla` evaluates the same points as SciPy's find_root, on every shared twin case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Chandrupatla(), ChandrupatlaScipyTwin(), case)
