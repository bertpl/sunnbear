"""These tests check `Pegasus` against mpmath's Pegasus method through `PegasusMpmathTwin`."""

import pytest

from sunnbear.solvers import Pegasus
from tests.solvers.twins import assert_agrees_with_twin

from .mpmath_twin import PegasusMpmathTwin


@pytest.mark.parametrize("test_case", PegasusMpmathTwin.comparable_test_cases(), ids=str)
def test_pegasus_agrees_with_mpmath_pegasus(test_case):
    """`Pegasus` evaluates the same x-values as mpmath's Pegasus method, on the twin's comparable test cases."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Pegasus(), PegasusMpmathTwin(), test_case)
