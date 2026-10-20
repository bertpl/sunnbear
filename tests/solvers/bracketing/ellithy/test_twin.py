"""These tests check `Ellithy` against the authors' package hybridroots through `EllithyHybridrootsTwin`."""

import pytest

from sunnbear.solvers import Ellithy, EllithyVariant
from tests.solvers.twins import assert_agrees_with_twin

from .hybridroots_twin import EllithyHybridrootsTwin


@pytest.mark.parametrize("variant", EllithyVariant)
@pytest.mark.parametrize("test_case", EllithyHybridrootsTwin.compared_test_cases(), ids=str)
def test_ellithy_agrees_with_hybridroots(test_case, variant):
    """In every variant, `Ellithy` evaluates the same x-values as the function of hybridroots that implements its
    method, on every test case of `TWIN_TEST_CASES`."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Ellithy(variant=variant), EllithyHybridrootsTwin(variant=variant), test_case)
