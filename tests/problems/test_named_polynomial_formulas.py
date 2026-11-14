"""Each named polynomial formula (category 2.2) gives the expected candidates, on intervals with a sign change."""

import itertools
import math

import numpy as np
import pytest
from scipy import special

from sunnbear._core.problems.catalog.c02_standard_function_families.c02_named_polynomials.helpers import (
    jacobi_interval_bounds,
)
from sunnbear._core.problems.core import Formula, FormulaRegistry


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


# Each entry holds a named polynomial formula's number, its number of candidates, and the function that gives the
# formula's value from scipy.
NAMED_POLYNOMIAL_FORMULAS = [
    pytest.param((2, 2, 1), 42, _chebyshev_first_kind, id="chebyshev_first_kind"),
    pytest.param((2, 2, 2), 42, _chebyshev_second_kind, id="chebyshev_second_kind"),
    pytest.param((2, 2, 3), 42, _legendre, id="legendre"),
    pytest.param((2, 2, 4), 42 * 13, _gegenbauer, id="gegenbauer"),
    pytest.param((2, 2, 5), 42 * 6 * 6, _jacobi, id="jacobi"),
]

# The degrees at which `test_every_formula_agrees_with_scipy` compares a formula with scipy.
COMPARED_DEGREES = (1.0, 2.0, 3.0, 8.0, 31.0, 64.0, 129.0, 1024.0)


def _formula_with_number(formula_number: tuple[int, ...]) -> Formula:
    """Return the registered formula with `formula_number`."""
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]
    return formula


def test_the_parametrization_names_every_named_polynomial_formula():
    """`NAMED_POLYNOMIAL_FORMULAS` names exactly the formulas of category 2.2."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 2)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in NAMED_POLYNOMIAL_FORMULAS} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_candidates, scipy_fun", NAMED_POLYNOMIAL_FORMULAS)
def test_every_candidate_is_negative_at_its_lower_bound_and_positive_at_its_upper_bound(
    formula_number, n_candidates, scipy_fun
):
    """A formula gives its expected number of candidates, each with ``f(a) < 0 < f(b)`` at ``c = 0``."""
    # --- arrange ----------------------
    formula = _formula_with_number(formula_number)

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_candidates
    for candidate in candidates:
        assert candidate.xc_fun(candidate.a, 0.0) < 0.0 < candidate.xc_fun(candidate.b, 0.0), candidate.id


@pytest.mark.parametrize("formula_number, n_candidates, scipy_fun", NAMED_POLYNOMIAL_FORMULAS)
def test_the_interval_of_an_even_degree_leaves_out_1_zero(formula_number, n_candidates, scipy_fun):
    """Between -1 and the lower bound of an even degree's interval, the function changes sign exactly once."""
    # --- arrange ----------------------
    formula = _formula_with_number(formula_number)
    even_degree_candidates = [
        candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] % 2 == 0
    ]
    n_steps = 25

    # --- act / assert -----------------
    assert even_degree_candidates
    for candidate in even_degree_candidates:
        # x-values from -1 to the lower bound, at equal steps of the angle acos(-x), in which the zeros lie evenly
        angle_of_lower_bound = math.acos(-candidate.a)
        x_values = [-math.cos(angle_of_lower_bound * step / n_steps) for step in range(n_steps + 1)]
        is_positive = [value > 0.0 for x in x_values if (value := candidate.xc_fun(x, 0.0)) != 0.0]
        n_sign_changes = sum(1 for before, after in itertools.pairwise(is_positive) if before != after)
        assert n_sign_changes == 1, candidate.id


@pytest.mark.parametrize("formula_number, n_candidates, scipy_fun", NAMED_POLYNOMIAL_FORMULAS)
def test_every_formula_agrees_with_scipy(formula_number, n_candidates, scipy_fun):
    """At the degrees of `COMPARED_DEGREES`, a formula's value equals scipy's across the interval, for 3 values of c."""
    # --- arrange ----------------------
    formula = _formula_with_number(formula_number)
    compared_candidates = [
        candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] in COMPARED_DEGREES
    ]

    # --- act / assert -----------------
    assert {candidate.id.param_values[0] for candidate in compared_candidates} == set(COMPARED_DEGREES)
    for candidate in compared_candidates:
        for x in np.linspace(candidate.a, candidate.b, 7):
            for c in (0.0, 0.4, -0.3):
                expected = scipy_fun(float(x), c, *candidate.id.param_values)
                value = candidate.xc_fun(float(x), c)
                assert value == pytest.approx(expected, rel=1e-9, abs=1e-9), (candidate.id, x, c)


@pytest.mark.parametrize(
    "alpha, beta",
    [
        pytest.param(-0.99, -0.99, id="both_near_the_lower_limit"),
        pytest.param(-0.99, 3.0, id="alpha_near_the_lower_limit_beta_highest"),
        pytest.param(3.0, -0.99, id="alpha_highest_beta_near_the_lower_limit"),
        pytest.param(3.0, 3.0, id="both_highest"),
        pytest.param(6.5, 6.5, id="highest_alpha_of_the_gegenbauer_polynomial"),
    ],
)
def test_the_lower_bound_of_an_even_degree_lies_between_the_2_lowest_zeros(alpha, beta):
    """At the limits of the parameters that the formulas accept, the interval rule holds for every even degree tried."""
    for n in (2, 4, 6, 8, 16, 32, 64, 128, 1024):
        # --- arrange ----------------------
        zeros = np.sort(special.roots_jacobi(n, alpha, beta)[0])

        # --- act --------------------------
        a, b = jacobi_interval_bounds(float(n), alpha, beta)

        # --- assert -----------------------
        assert zeros[0] < a < zeros[1], n
        assert b == 1.0
