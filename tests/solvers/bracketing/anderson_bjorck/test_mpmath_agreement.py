"""These tests check `AndersonBjorck` against mpmath's Anderson-Björck method through `AndersonBjorckMpmathTwin`."""

import pytest

from sunnbear.solvers import AndersonBjorck
from tests.solvers.bracketing.anderson_bjorck.mpmath_twin import AndersonBjorckMpmathTwin
from tests.solvers.example_functions import steep_exponential
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


@pytest.mark.parametrize(
    "test_case", [test_case for test_case in TWIN_TEST_CASES if test_case.f is not steep_exponential], ids=str
)  # The docstring of AndersonBjorckMpmathTwin gives the reason for leaving out steep_exponential.
def test_anderson_bjorck_agrees_with_mpmath_anderson_bjorck(test_case):
    """`AndersonBjorck` evaluates the same points as mpmath's Anderson-Björck method, on the shared twin test cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(AndersonBjorck(), AndersonBjorckMpmathTwin(), test_case)
