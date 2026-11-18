"""The formulas of category 2.5 give the expected candidates, each changing sign in its interval.

Further tests cover how `Exponential` keeps full precision next to its root, where ``exp(x - c)`` rounds to 1, and
how `Logarithm` maps its bounds to -1 and 1 for every ``d``.
"""

import math

import pytest

from sunnbear._core.problems.core import FormulaRegistry

# Each entry holds an exponential or logarithm formula's number and its number of candidates.
EXPONENTIAL_AND_LOGARITHM_FORMULAS = [
    pytest.param((2, 5, 1), 151, id="exponential"),
    pytest.param((2, 5, 2), 150, id="logarithm"),
]


def test_the_parametrization_names_every_exponential_and_logarithm_formula():
    """`EXPONENTIAL_AND_LOGARITHM_FORMULAS` names exactly the formulas of category 2.5."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 5)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in EXPONENTIAL_AND_LOGARITHM_FORMULAS} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_candidates", EXPONENTIAL_AND_LOGARITHM_FORMULAS)
def test_every_candidate_has_opposite_signs_at_the_bounds_of_its_interval(formula_number, n_candidates):
    """A formula gives its expected number of candidates, and at ``c = 0`` each candidate is negative at one bound of
    its interval and positive at the other."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number(formula_number)

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_candidates
    for candidate in candidates:
        value_at_a, value_at_b = candidate.xc_fun(candidate.a, 0.0), candidate.xc_fun(candidate.b, 0.0)
        assert min(value_at_a, value_at_b) < 0.0 < max(value_at_a, value_at_b), candidate.id


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
