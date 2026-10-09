"""These tests check `Ridders` against `scipy.optimize.ridder` through `RiddersScipyTwin`."""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import RiddersScipyTwin


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize("test_case", RiddersScipyTwin.comparable_test_cases(), ids=str)
def test_ridders_agrees_with_scipy_ridder(test_case, variant):
    """In every variant, `Ridders` evaluates the same x-values as SciPy's ridder, on the twin's comparable test
    cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Ridders(variant=variant), RiddersScipyTwin(variant=variant), test_case)
