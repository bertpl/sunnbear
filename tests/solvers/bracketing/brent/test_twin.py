"""These tests check `Brent` against `scipy.optimize.brentq` and `scipy.optimize.brenth` through `BrentScipyTwin`."""

import pytest

from sunnbear.solvers import Brent, BrentVariant
from tests.solvers.twins import assert_agrees_with_twin

from .scipy_twin import BrentScipyTwin


@pytest.mark.parametrize("variant", BrentVariant)
@pytest.mark.parametrize("test_case", BrentScipyTwin.compared_test_cases(), ids=str)
def test_brent_agrees_with_scipy_brentq_and_brenth(test_case, variant):
    """In each variant, `Brent` evaluates the same x-values as the function of SciPy that implements its method,
    brentq or brenth, on every test case of `TWIN_TEST_CASES` that the twin does not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Brent(variant=variant), BrentScipyTwin(variant=variant), test_case)
