"""These tests check `Illinois` against mpmath's Illinois method through `IllinoisMpmathTwin`."""

import pytest

from sunnbear.solvers import Illinois
from tests.solvers.bracketing.illinois.mpmath_twin import IllinoisMpmathTwin
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("test_case", TWIN_TEST_CASES, ids=str)
def test_illinois_agrees_with_mpmath_illinois(test_case):
    """`Illinois` evaluates the same points as mpmath's Illinois method, on every shared twin test case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Illinois(), IllinoisMpmathTwin(), test_case)
