"""The hyperbolic function formulas (category 2.4) give the expected candidates, each changing sign in its interval.

Further tests cover how `HyperbolicTangent` keeps full precision next to its root, both at ``d = 1`` and in the
lower tail of ``tanh``.
"""

import math

import mpmath
import pytest

from sunnbear._core.problems.core import FormulaRegistry

# The reference values that mpmath computes use this many decimal digits.
MPMATH_DIGITS = 50

# Each entry holds a hyperbolic function formula's number and its number of candidates.
#
# `HyperbolicTangent` has 161 candidates that sweep the interval's bound, and 151 that sweep the level of the root.
HYPERBOLIC_FUNCTION_FORMULAS = [
    pytest.param((2, 4, 1), 151, id="hyperbolic_sine"),
    pytest.param((2, 4, 2), 151, id="hyperbolic_cosine"),
    pytest.param((2, 4, 3), 161 + 151, id="hyperbolic_tangent"),
    pytest.param((2, 4, 4), 161, id="inverse_hyperbolic_sine"),
    pytest.param((2, 4, 5), 150, id="inverse_hyperbolic_cosine"),
    pytest.param((2, 4, 6), 141, id="inverse_hyperbolic_tangent"),
]


def test_the_parametrization_names_every_hyperbolic_function_formula():
    """`HYPERBOLIC_FUNCTION_FORMULAS` names exactly the formulas of category 2.4."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 4)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in HYPERBOLIC_FUNCTION_FORMULAS} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_candidates", HYPERBOLIC_FUNCTION_FORMULAS)
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


@pytest.mark.parametrize("c", [0.0, 0.3, -0.7])
def test_hyperbolic_tangent_at_level_1_has_the_sign_of_x_minus_c_next_to_its_root(c):
    """At ``d = 1``, `HyperbolicTangent` is 0 at its root ``x = c`` and has the sign of ``x - c`` at the floats next
    to it, where ``1 + tanh(x - c)`` rounds to 1."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 4, 3))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[1] == 1.0]

    # --- act / assert -----------------
    assert len(candidates) == 161 + 1  # the 1 of the sweep of levels at d = 1 too
    for candidate in candidates:
        assert candidate.xc_fun(c, c) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, -math.inf), c) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, math.inf), c) > 0.0, candidate.id


def test_hyperbolic_tangent_keeps_full_precision_at_every_level_of_its_root():
    """At every level ``d`` of the root, `HyperbolicTangent` agrees with ``1 + tanh(x) - d`` from mpmath at x-values
    around the root, to within a few ulps of the larger of ``1 + tanh(x)`` and ``d``.

    Computed as written, ``1 + tanh(x)`` has an error of about 1e-16 whatever its size, which next to a root at
    ``d = 10^-15`` is about 10 % of ``d``.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 4, 3))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.b == 32.0]

    # --- act / assert -----------------
    assert len(candidates) == 151
    with mpmath.workdps(MPMATH_DIGITS):
        for candidate in candidates:
            [_, d] = candidate.id.param_values
            root = math.atanh(d - 1.0)
            for x in (root - 1.0, root - 1e-6, root, root + 1e-6, root + 1.0):
                one_plus_tanh = 1 + mpmath.tanh(mpmath.mpf(x))
                expected = float(one_plus_tanh - d)
                max_error = 8 * math.ulp(max(float(one_plus_tanh), d))
                assert abs(candidate.xc_fun(x, 0.0) - expected) <= max_error, (candidate.id, x)
