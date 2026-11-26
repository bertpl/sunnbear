"""These tests cover what the trigonometric function formulas (category 2.6) add to the plain functions:

- the precision of `Cosine` and `InverseTangent` next to the root, where subtracting 2 nearly equal values would cancel
  their leading digits;
- the sign changes of `TangentAcrossPoles`, and its finite values at its poles.
"""

import itertools
import math

import mpmath
import pytest

from sunnbear._core.problems.core import FormulaRegistry

# mpmath computes the reference values with this many decimal digits.
MPMATH_DIGITS = 50


def test_cosine_keeps_full_precision_next_to_its_root():
    """At ``c = 0`` and every ``d``, `Cosine` agrees with ``cos(pi*x/2) - cos(pi*d/2)`` from mpmath next to its root
    ``x = d``, to within a relative 1e-8.

    The tolerance covers the rounding of ``pi*x/2``, which at a relative distance of 1e-6 from the root changes
    ``pi*x/2 - pi*d/2`` by up to about 1e-10 of its value.

    Computed as the difference of 2 cosines, the function would have an error of about 1e-16, which at ``d = 2^-30`` is
    about 5e7 times its value at a relative distance of 1e-6 from the root.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 6, 2))

    # --- act / assert -----------------
    with mpmath.workdps(MPMATH_DIGITS):
        for candidate in formula.build_all_candidates():
            [d] = candidate.id.param_values
            for x in (0.5 * d, d * (1.0 - 1e-6), d * (1.0 + 1e-6), 1.5 * d):
                half_pi = mpmath.pi / 2
                expected = float(mpmath.cos(half_pi * mpmath.mpf(x)) - mpmath.cos(half_pi * mpmath.mpf(d)))
                assert candidate.xc_fun(x, 0.0) == pytest.approx(expected, rel=1e-8, abs=0.0), (candidate.id, x)


@pytest.mark.parametrize("c", [0.0, 0.3, -0.7])
def test_inverse_tangent_at_d_equal_to_1_has_the_sign_of_x_minus_c_next_to_its_root(c):
    """At ``d = 1``, `InverseTangent` is 0 at its root ``x = c`` and has the sign of ``x - c`` at the floats next to
    the root."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 6, 6))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[1] == 1.0]

    # --- act / assert -----------------
    assert len(candidates) == 241  # the sweep of d ends at b = 2^30, d = 1, which the sweep of b holds too
    for candidate in candidates:
        assert candidate.xc_fun(c, c) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, -math.inf), c) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(c, math.inf), c) > 0.0, candidate.id


def test_inverse_tangent_keeps_full_precision_across_the_sweep_of_d():
    """At every ``d`` in the sweep of ``d``, `InverseTangent` agrees with ``(2/pi)*atan(x) + 1 - d`` from mpmath at
    x-values around the root, to within a few ulps of the larger of ``(2/pi)*atan(x) + 1`` and ``d``.

    If it were computed by adding 1 to ``(2/pi)*atan(x)``, ``(2/pi)*atan(x) + 1`` would have an error of about 1e-16
    whatever its size, which next to a root at ``d = 2^-30`` is about 1e-7 of ``d``.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 6, 6))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.b == 2.0**30]

    # --- act / assert -----------------
    assert len(candidates) == 121
    with mpmath.workdps(MPMATH_DIGITS):
        for candidate in candidates:
            [_, d] = candidate.id.param_values
            root = math.tan(0.5 * math.pi * (d - 1.0))
            for x in (root - 1.0, root * (1.0 - 1e-6), root, root * (1.0 + 1e-6), root + 1.0):
                one_plus_scaled_atan = 1 + 2 * mpmath.atan(mpmath.mpf(x)) / mpmath.pi
                expected = float(one_plus_scaled_atan - d)
                max_error = 8 * math.ulp(max(float(one_plus_scaled_atan), d))
                assert abs(candidate.xc_fun(x, 0.0) - expected) <= max_error, (candidate.id, x)


def test_tangent_across_poles_changes_sign_2_n_plus_1_times():
    """At ``c = 0``, `TangentAcrossPoles` changes sign ``2*n + 1`` times on its interval: at its roots and at its
    poles.

    The x-values lie 0.1 apart, none on an integer, so that each root and pole lies between 2 of them. The test covers
    the candidates with ``n`` up to 64, which keeps it fast.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 6, 4))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] <= 64]

    # --- act / assert -----------------
    for candidate in candidates:
        [n] = candidate.id.param_values
        n_x_values = round(10 * (candidate.b - candidate.a))
        x_values = [candidate.a, *(candidate.a + 0.1 * (i + 0.5) for i in range(n_x_values)), candidate.b]
        signs = [math.copysign(1.0, candidate.xc_fun(x, 0.0)) for x in x_values]
        n_sign_changes = sum(1 for sign_before, sign_after in itertools.pairwise(signs) if sign_before != sign_after)
        assert n_sign_changes == 2 * n + 1, candidate.id


def test_tangent_across_poles_is_finite_at_its_poles():
    """At ``c = 0``, `TangentAcrossPoles` is finite at each of its poles, the odd integers of its interval, and larger
    than 1e10 there."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 6, 4))

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        [n] = candidate.id.param_values
        for k in range(-int(n), int(n) + 1):
            if k % 2 != 0:
                value = candidate.xc_fun(float(k), 0.0)
                assert math.isfinite(value), (candidate.id, k)
                assert abs(value) > 1e10, (candidate.id, k)
