"""The named polynomial formulas (category 2.2) give the expected candidates, with values that agree with a reference.

Each candidate's interval has a sign change, and the interval of an even degree leaves out exactly the lowest zero.
"""

import itertools
import math

import mpmath
import numpy as np
import pytest
from scipy import special

from sunnbear._core.problems.catalog.c02_standard_function_families.c02_named_polynomials import (
    f04_gegenbauer_polynomial,
    f05_jacobi_polynomial,
    f06_hermite_polynomial,
    f07_laguerre_polynomial,
)
from sunnbear._core.problems.catalog.c02_standard_function_families.c02_named_polynomials.helpers import (
    jacobi_interval_bounds,
)
from sunnbear._core.problems.core import FormulaRegistry

# The reference functions that use mpmath compute with this many decimal digits.
MPMATH_DIGITS = 50


def _chebyshev_first_kind(x: float, c: float, n: float) -> float:
    """Return scipy's ``T_n(x) + c``."""
    return special.eval_chebyt(int(n), x) + c


def _chebyshev_second_kind(x: float, c: float, n: float) -> float:
    """Return scipy's ``U_n(x - c/n^2)``."""
    return special.eval_chebyu(int(n), x - c / n**2)


def _legendre(x: float, c: float, n: float) -> float:
    """Return scipy's ``P_n(x - c/n^2)``."""
    return special.eval_legendre(int(n), x - c / n**2)


def _jacobi(x: float, c: float, n: float, alpha: float, beta: float) -> float:
    """Return scipy's Jacobi polynomial at ``x - c/n^2``, divided by its value at 1."""
    return special.eval_jacobi(int(n), alpha, beta, x - c / n**2) / special.eval_jacobi(int(n), alpha, beta, 1.0)


def _gegenbauer(x: float, c: float, n: float, alpha: float) -> float:
    """Return the divided Gegenbauer polynomial at ``x - c/n^2``, as scipy's divided Jacobi polynomial.

    scipy's Gegenbauer polynomial is 0 everywhere at ``alpha = 0``, so it cannot be divided by its value at 1.
    """
    return _jacobi(x, c, n, alpha - 0.5, alpha - 0.5)


def _hermite(x: float, c: float, n: float) -> float:
    """Return scipy's ``H_n(x - c)``, divided by its norm ``sqrt(2^n * n! * sqrt(pi))``."""
    norm = math.sqrt(2.0**n * math.factorial(int(n)) * math.sqrt(math.pi))
    return special.eval_hermite(int(n), x - c) / norm


def _laguerre(x: float, c: float, n: float) -> float:
    """Return scipy's ``L_n(x - c)``."""
    return special.eval_laguerre(int(n), x - c)


def _bernoulli(x: float, c: float, n: float, a: float, b: float) -> float:
    """Return mpmath's ``B_n(x - c)``."""
    with mpmath.workdps(MPMATH_DIGITS):
        return float(mpmath.bernpoly(int(n), mpmath.mpf(x) - mpmath.mpf(c)))


def _wilkinson(x: float, c: float, n: float) -> float:
    """Return the product over ``k = 1..n`` of ``(y - k)/k`` at ``y = x - c``, as mpmath's ``binomial(y - 1, n)``."""
    with mpmath.workdps(MPMATH_DIGITS):
        return float(mpmath.binomial(mpmath.mpf(x) - mpmath.mpf(c) - 1, int(n)))


def _second_wilkinson(x: float, c: float, n: float) -> float:
    """Return the product over ``k = 1..n`` of ``(x - 2^-(k + c))``, through mpmath's q-Pochhammer symbol.

    The product equals ``x^n`` times the product over ``k = 0..n-1`` of ``(1 - z*q^k)``, with ``z = 2^-(1 + c)/x`` and
    ``q = 1/2``, and that second product is the q-Pochhammer symbol.
    """
    with mpmath.workdps(MPMATH_DIGITS):
        x_exact = mpmath.mpf(x)
        z = mpmath.mpf(2) ** (-(1 + mpmath.mpf(c))) / x_exact
        return float(x_exact ** int(n) * mpmath.qp(z, mpmath.mpf(1) / 2, int(n)))


def _bernoulli_amplitude(n: float, a: float, b: float) -> float:
    """Return ``2*n!/(2*pi)^n``, the amplitude of ``B_n`` between its outermost real zeros."""
    return 2.0 * math.factorial(int(n)) / (2.0 * math.pi) ** n


# Each entry holds, for a named polynomial formula:
# - its number;
# - its number of candidates;
# - the function that gives the formula's value from scipy or mpmath;
# - the function that gives the scale of a candidate's values near its zeros, from its parameters.
#
# `test_every_formula_agrees_with_its_reference` scales its absolute tolerance by that scale. For a formula that is a
# product of factors, the scale is 0, so only the relative tolerance applies: its values span many orders of magnitude,
# and each is accurate relative to its own size.
NAMED_POLYNOMIAL_FORMULAS = [
    pytest.param((2, 2, 1), 42, _chebyshev_first_kind, lambda *params: 1.0, id="chebyshev_first_kind"),
    pytest.param((2, 2, 2), 42, _chebyshev_second_kind, lambda *params: 1.0, id="chebyshev_second_kind"),
    pytest.param((2, 2, 3), 42, _legendre, lambda *params: 1.0, id="legendre"),
    pytest.param((2, 2, 4), 42 * 13, _gegenbauer, lambda *params: 1.0, id="gegenbauer"),
    pytest.param((2, 2, 5), 42 * 6 * 6, _jacobi, lambda *params: 1.0, id="jacobi"),
    pytest.param((2, 2, 6), 40, _hermite, lambda *params: 1.0, id="hermite"),
    pytest.param((2, 2, 7), 20, _laguerre, lambda *params: 1.0, id="laguerre"),
    pytest.param((2, 2, 8), 12 + 8 + 5, _bernoulli, _bernoulli_amplitude, id="bernoulli"),
    pytest.param((2, 2, 9), 40, _wilkinson, lambda *params: 0.0, id="wilkinson"),
    pytest.param((2, 2, 10), 20, _second_wilkinson, lambda *params: 0.0, id="second_wilkinson"),
]

# `test_every_formula_agrees_with_its_reference` compares a formula with its reference at those of these degrees
# that the formula sweeps.
COMPARED_DEGREES = (1.0, 2.0, 3.0, 8.0, 20.0, 21.0, 31.0, 40.0, 49.0, 64.0, 129.0, 1024.0)

# `test_the_lower_bound_of_an_even_degree_lies_between_the_2_lowest_zeros` checks the interval rule at these Jacobi
# parameters: just above the excluded lower limit of ``alpha`` and ``beta``, at their upper limit, and at the upper
# limit of `GegenbauerPolynomial`, whose ``alpha`` is 0.5 higher than the Jacobi parameters.
NEAR_LOWER_LIMIT = f05_jacobi_polynomial.ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT + 0.01
JACOBI_UPPER_LIMIT = f05_jacobi_polynomial.ALPHA_BETA_INCLUSIVE_UPPER_LIMIT
GEGENBAUER_UPPER_LIMIT = f04_gegenbauer_polynomial.ALPHA_INCLUSIVE_UPPER_LIMIT - 0.5


def test_the_parametrization_names_every_named_polynomial_formula():
    """`NAMED_POLYNOMIAL_FORMULAS` names exactly the formulas of category 2.2."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 2)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in NAMED_POLYNOMIAL_FORMULAS} == formula_numbers_in_category


@pytest.mark.parametrize(
    "formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun", NAMED_POLYNOMIAL_FORMULAS
)
def test_every_candidate_has_opposite_signs_at_the_bounds_of_its_interval(
    formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun
):
    """A formula gives its expected number of candidates, each with opposite signs at its 2 bounds at ``c = 0``."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_candidates
    for candidate in candidates:
        value_at_a, value_at_b = candidate.xc_fun(candidate.a, 0.0), candidate.xc_fun(candidate.b, 0.0)
        assert min(value_at_a, value_at_b) < 0.0 < max(value_at_a, value_at_b), candidate.id


@pytest.mark.parametrize(
    "formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun", NAMED_POLYNOMIAL_FORMULAS
)
def test_the_interval_of_an_even_degree_leaves_out_1_zero(
    formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun
):
    """From the lower bound of the next odd degree's interval to an even degree's lower bound, the sign changes once."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]
    even_degree_candidates = [
        candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] % 2 == 0
    ]
    n_steps = 25

    # --- act / assert -----------------
    for candidate in even_degree_candidates:
        # The interval of the next odd degree holds every zero of that degree, and its lower bound lies below every
        # zero of this even degree too.
        n, *other_params = candidate.id.param_values
        x_lowest = formula.interval_bounds(n + 1.0, *other_params)[0]
        x_values = [x_lowest + (candidate.a - x_lowest) * step / n_steps for step in range(n_steps + 1)]
        is_positive_per_x = [value > 0.0 for x in x_values if (value := candidate.xc_fun(x, 0.0)) != 0.0]
        n_sign_changes = sum(1 for before, after in itertools.pairwise(is_positive_per_x) if before != after)
        assert n_sign_changes == 1, candidate.id


@pytest.mark.parametrize(
    "formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun", NAMED_POLYNOMIAL_FORMULAS
)
def test_every_formula_agrees_with_its_reference(formula_number, n_candidates, reference_fun, abs_tolerance_scale_fun):
    """At each degree of `COMPARED_DEGREES`, a formula equals its reference across the interval, for 3 values of c."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]
    compared_candidates = [
        candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] in COMPARED_DEGREES
    ]

    # --- act / assert -----------------
    # Each formula sweeps only some of `COMPARED_DEGREES`; requiring 4 of them keeps a recipe change from leaving the
    # comparison with almost no degrees.
    assert len({candidate.id.param_values[0] for candidate in compared_candidates}) >= 4
    for candidate in compared_candidates:
        abs_tolerance = 1e-9 * abs_tolerance_scale_fun(*candidate.id.param_values)
        for x in np.linspace(candidate.a, candidate.b, 7):
            for c in (0.0, 0.4, -0.3):
                expected = reference_fun(float(x), c, *candidate.id.param_values)
                value = candidate.xc_fun(float(x), c)
                assert value == pytest.approx(expected, rel=1e-9, abs=abs_tolerance), (candidate.id, x, c)


@pytest.mark.parametrize("n", [2, 4, 6, 8, 16, 32, 64, 128, 1024])
@pytest.mark.parametrize(
    "alpha, beta",
    [
        pytest.param(NEAR_LOWER_LIMIT, NEAR_LOWER_LIMIT, id="both_near_the_lower_limit"),
        pytest.param(NEAR_LOWER_LIMIT, JACOBI_UPPER_LIMIT, id="alpha_near_the_lower_limit_beta_highest"),
        pytest.param(JACOBI_UPPER_LIMIT, NEAR_LOWER_LIMIT, id="alpha_highest_beta_near_the_lower_limit"),
        pytest.param(JACOBI_UPPER_LIMIT, JACOBI_UPPER_LIMIT, id="both_highest"),
        pytest.param(GEGENBAUER_UPPER_LIMIT, GEGENBAUER_UPPER_LIMIT, id="highest_alpha_of_the_gegenbauer_polynomial"),
    ],
)
def test_the_lower_bound_of_an_even_degree_lies_between_the_2_lowest_zeros(alpha, beta, n):
    """At the limits of the formulas' valid parameters, the interval rule holds for an even degree."""
    # --- arrange ----------------------
    zeros = np.sort(special.roots_jacobi(n, alpha, beta)[0])

    # --- act --------------------------
    a, b = jacobi_interval_bounds(float(n), alpha, beta)

    # --- assert -----------------------
    assert zeros[0] < a < zeros[1]
    assert b == 1.0


@pytest.mark.parametrize(
    "formula_number, scipy_roots_fun, highest_valid_degree",
    [
        pytest.param((2, 2, 6), special.roots_hermite, f06_hermite_polynomial.HIGHEST_VALID_DEGREE, id="hermite"),
        pytest.param((2, 2, 7), special.roots_laguerre, f07_laguerre_polynomial.HIGHEST_VALID_DEGREE, id="laguerre"),
    ],
)
def test_the_interval_rule_holds_up_to_the_highest_valid_degree(formula_number, scipy_roots_fun, highest_valid_degree):
    """Up to its highest valid degree, a formula's interval holds every zero that scipy gives, except the lowest zero of
    an even degree, and its values at the bounds are finite."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]
    degrees = [2, 3, 4, 8, 16, 33, 64, 128, highest_valid_degree - 1, highest_valid_degree]

    # --- act / assert -----------------
    for n in degrees:
        zeros = np.sort(scipy_roots_fun(n)[0])
        a, b = formula.interval_bounds(float(n))
        values_at_bounds = [formula.bind_xc_fun((float(n),))(bound, 0.0) for bound in (a, b)]
        if n % 2 == 0:
            assert zeros[0] < a < zeros[1], n
        else:
            assert a < zeros[0], n
        assert zeros[-1] < b, n
        assert all(math.isfinite(value) for value in values_at_bounds), n


def test_every_real_zero_of_a_bernoulli_candidate_lies_well_inside_its_interval():
    """A Bernoulli candidate is positive from 0.25 below its upper bound to 3 above it, so no real zero lies there."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == (2, 2, 8)]

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        x_values = np.linspace(candidate.b - 0.25, candidate.b + 3.0, 60)
        for x in x_values:
            assert candidate.xc_fun(float(x), 0.0) > 0.0, (candidate.id, x)
