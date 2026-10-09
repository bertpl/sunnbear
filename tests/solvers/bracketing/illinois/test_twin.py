"""These tests check `Illinois` against mpmath's Illinois method through `IllinoisMpmathTwin`."""

import pytest

from sunnbear.solvers import Illinois
from tests.solvers.twins import assert_agrees_with_twin

from .mpmath_twin import IllinoisMpmathTwin


@pytest.mark.parametrize("test_case", IllinoisMpmathTwin.compared_test_cases(), ids=str)
def test_illinois_agrees_with_mpmath_illinois(test_case):
    """`Illinois` evaluates the same x-values as mpmath's Illinois method, on every test case of `TWIN_TEST_CASES` that
    the twin does not exclude."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Illinois(), IllinoisMpmathTwin(), test_case)
