"""`HyperbolicCosine` and `HyperbolicTangent` keep full precision next to the root, where subtracting 2 nearly equal
values would cancel their leading digits.
"""

import math

import mpmath
import pytest

from sunnbear._core.problems.core import FormulaRegistry

# mpmath computes the reference values with this many decimal digits.
MPMATH_DIGITS = 50


def test_hyperbolic_cosine_has_the_sign_of_x_minus_its_root_next_to_its_root():
    """At ``c = 0``, `HyperbolicCosine` is 0 at its root ``x = b/2`` and nonzero at the floats next to it, also where
    ``cosh(x)`` and ``cosh(b/2)`` round to the same float."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 4, 2))

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        root = 0.5 * candidate.b
        assert candidate.xc_fun(root, 0.0) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(root, -math.inf), 0.0) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(root, math.inf), 0.0) > 0.0, candidate.id


@pytest.mark.parametrize("c", [0.0, 0.3, -0.7])
def test_hyperbolic_tangent_at_d_equal_to_1_has_the_sign_of_x_minus_c_next_to_its_root(c):
    """At ``d = 1``, `HyperbolicTangent` is 0 at its root ``x = c`` and has the sign of ``x - c`` at the floats next
    to it, where ``1 + tanh(x - c)`` rounds to 1."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 4, 3))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[1] == 1.0]

    # --- act / assert -----------------
    assert len(candidates) == 161 + 1  # 161 from the sweep of b, and 1 from the sweep of d, which ends at d = 1
    for candidate in candidates:
        assert candidate.xc_fun(c, c) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, -math.inf), c) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, math.inf), c) > 0.0, candidate.id


def test_hyperbolic_tangent_keeps_full_precision_across_the_sweep_of_d():
    """At every ``d`` in the sweep of ``d``, `HyperbolicTangent` agrees with ``1 + tanh(x) - d`` from mpmath at x-values
    around the root, to within a few ulps of the larger of ``1 + tanh(x)`` and ``d``.

    Computed by adding 1 to ``tanh(x)``, ``1 + tanh(x)`` has an error of about 1e-16 whatever its size, which next to
    a root at ``d = 10^-15`` is about 10 % of ``d``.
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
