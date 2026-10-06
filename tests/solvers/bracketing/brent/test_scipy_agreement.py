"""These tests check `Brent` against `scipy.optimize.brentq` through `BrentScipyTwin`."""

import pytest

from sunnbear.solvers import Brent
from tests.solvers.bracketing.brent.scipy_twin import BrentScipyTwin
from tests.solvers.twins import TWIN_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("case", TWIN_CASES, ids=str)
def test_brent_agrees_with_scipy_brentq(case):
    """`Brent` evaluates the same points as SciPy's brentq, on every shared twin case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Brent(), BrentScipyTwin(), case)
