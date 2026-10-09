"""These tests check `AndersonBjorck` against mpmath's Anderson-Björck method through `AndersonBjorckMpmathTwin`."""

import pytest

from sunnbear.solvers import AndersonBjorck
from tests.solvers.twins import assert_agrees_with_twin

from .mpmath_twin import AndersonBjorckMpmathTwin


@pytest.mark.parametrize("test_case", AndersonBjorckMpmathTwin.comparable_test_cases(), ids=str)
def test_anderson_bjorck_agrees_with_mpmath_anderson_bjorck(test_case):
    """`AndersonBjorck` evaluates the same x-values as mpmath's Anderson-Björck method, on the twin's comparable test
    cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(AndersonBjorck(), AndersonBjorckMpmathTwin(), test_case)
