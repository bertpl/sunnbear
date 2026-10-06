"""These tests check `Pegasus` against mpmath's Pegasus method through `PegasusMpmathTwin`."""

import pytest

from sunnbear.solvers import Pegasus
from tests.solvers.bracketing.pegasus.mpmath_twin import PegasusMpmathTwin
from tests.solvers.twins import TWIN_TEST_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("test_case", TWIN_TEST_CASES, ids=str)
def test_pegasus_agrees_with_mpmath_pegasus(test_case):
    """`Pegasus` evaluates the same points as mpmath's Pegasus method, on every shared twin test case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Pegasus(), PegasusMpmathTwin(), test_case)
