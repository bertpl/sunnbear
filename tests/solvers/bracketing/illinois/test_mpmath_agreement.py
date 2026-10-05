"""These tests check `Illinois` against mpmath's Illinois method through `IllinoisMpmathTwin`."""

import pytest

from sunnbear.solvers import Illinois
from tests.solvers.bracketing.illinois.mpmath_twin import IllinoisMpmathTwin
from tests.solvers.twins import TWIN_CASES, assert_agrees_with_twin


@pytest.mark.parametrize("case", TWIN_CASES, ids=str)
def test_illinois_agrees_with_mpmath_illinois(case):
    """`Illinois` evaluates the same points as mpmath's Illinois method, on every shared twin case."""
    # --- act / assert -----------------
    assert_agrees_with_twin(Illinois(), IllinoisMpmathTwin(), case)
