"""`Exponential` keeps full precision next to its root, where ``exp(x - c)`` rounds to 1, and `Logarithm` maps its
bounds to -1 and 1 for every ``d``.
"""

import math

import pytest

from sunnbear._core.problems.core import FormulaRegistry


@pytest.mark.parametrize("c", [0.0, 0.05, -0.07])
def test_exponential_has_the_sign_of_x_minus_c_next_to_its_root(c):
    """`Exponential` is 0 at its root ``x = c`` and has the sign of ``x - c`` at the floats next to the root, where
    ``exp(x - c)`` rounds to 1."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 5, 1))

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        assert candidate.xc_fun(c, c) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, -math.inf), c) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, math.inf), c) > 0.0, candidate.id


@pytest.mark.parametrize("c", [0.0, 0.5, -0.5])
def test_logarithm_is_minus_1_plus_c_and_1_plus_c_at_its_bounds_and_0_at_its_root(c):
    """For every ``d``, `Logarithm` takes these values, each to within 1e-15:

    - ``-1 + c`` at ``x = d``;
    - ``1 + c`` at ``x = 1``;
    - 0 at its root ``x = d^((1 + c)/2)``.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 5, 2))

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        d = candidate.a
        root = d ** ((1.0 + c) / 2.0)
        assert candidate.xc_fun(d, c) == pytest.approx(-1.0 + c, abs=1e-15), candidate.id
        assert candidate.xc_fun(1.0, c) == pytest.approx(1.0 + c, abs=1e-15), candidate.id
        assert candidate.xc_fun(root, c) == pytest.approx(0.0, abs=1e-15), candidate.id
