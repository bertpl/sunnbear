"""Every formula of category 2 gives its expected number of candidates, each changing sign in its interval."""

import pytest

from sunnbear._core.problems.core import FormulaRegistry

# Each entry holds a formula's number and its number of candidates.
#
# - A simple polynomial (2.1) combines every value of its first parameter, a power or a term count, with every value of
#   its second, a weight or a slope.
# - `NearEdgePower` (2.3.3) has 81 candidates whose interval starts at the edge of the power's domain, and 63 whose
#   interval starts near it.
# - `NearPolePower` (2.3.4) sweeps 81 powers at each of 6 distances from the pole to the lower bound, of which 63 pairs
#   have no root inside the interval.
# - `HyperbolicTangent` (2.4.3) has 161 candidates from the sweep of ``b``, and 151 from the sweep of ``d``.
# - `Sine` (2.6.1) has 219 candidates from the sweep of a small ``b`` and 112 from the odd values of a large ``b``; both
#   recipes hold ``b = 1``, which counts once. `InverseSine` (2.6.5) has 1 at ``d = 0`` and 300 from the sweep of ``d``.
# - `InverseTangent` (2.6.6) has 241 candidates from the sweep of ``b`` and 121 from the sweep of ``d``; both sweeps
#   hold ``b = 2^30``, ``d = 1``, which counts once.
CANDIDATE_COUNTS = [
    pytest.param((2, 1, 1), 1, id="linear"),
    pytest.param((2, 1, 2), 5 * 31, id="linear_plus_even_power"),
    pytest.param((2, 1, 3), 4 * 43, id="linear_plus_odd_power"),
    pytest.param((2, 1, 4), 4 * 31, id="linear_plus_sum_of_even_powers"),
    pytest.param((2, 1, 5), 3 * 43, id="linear_plus_sum_of_odd_powers"),
    pytest.param((2, 1, 6), 9 * 25, id="one_sided_linear_plus_power"),
    pytest.param((2, 2, 1), 180, id="chebyshev_first_kind"),
    pytest.param((2, 2, 2), 180, id="chebyshev_second_kind"),
    pytest.param((2, 2, 3), 180, id="legendre"),
    pytest.param((2, 2, 4), 60 * 13, id="gegenbauer"),
    pytest.param((2, 2, 5), 14 * 10 * 10, id="jacobi"),
    pytest.param((2, 2, 6), 45, id="hermite"),
    pytest.param((2, 2, 7), 23, id="laguerre"),
    pytest.param((2, 2, 8), 12 + 8 + 5, id="bernoulli"),
    pytest.param((2, 2, 9), 63, id="wilkinson"),
    pytest.param((2, 2, 10), 20, id="second_wilkinson"),
    pytest.param((2, 3, 1), 121, id="signed_power_1"),
    pytest.param((2, 3, 2), 121, id="signed_power_2"),
    pytest.param((2, 3, 3), 81 + 63, id="near_edge_power"),
    pytest.param((2, 3, 4), 81 * 6 - 63, id="near_pole_power"),
    pytest.param((2, 3, 5), 61, id="signed_reciprocal_power"),
    pytest.param((2, 4, 1), 151, id="hyperbolic_sine"),
    pytest.param((2, 4, 2), 151, id="hyperbolic_cosine"),
    pytest.param((2, 4, 3), 161 + 151, id="hyperbolic_tangent"),
    pytest.param((2, 4, 4), 161, id="inverse_hyperbolic_sine"),
    pytest.param((2, 4, 5), 150, id="inverse_hyperbolic_cosine"),
    pytest.param((2, 4, 6), 141, id="inverse_hyperbolic_tangent"),
    pytest.param((2, 5, 1), 151, id="exponential"),
    pytest.param((2, 5, 2), 150, id="logarithm"),
    pytest.param((2, 6, 1), 219 + 112 - 1, id="sine"),
    pytest.param((2, 6, 2), 301, id="cosine"),
    pytest.param((2, 6, 3), 300, id="tangent_between_poles"),
    pytest.param((2, 6, 4), 264, id="tangent_across_poles"),
    pytest.param((2, 6, 5), 1 + 300, id="inverse_sine"),
    pytest.param((2, 6, 6), 241 + 121 - 1, id="inverse_tangent"),
]


def test_the_parametrization_names_every_formula_of_category_2():
    """`CANDIDATE_COUNTS` names exactly the formulas of category 2."""
    # --- act --------------------------
    formula_numbers_in_category = {formula.number for formula in FormulaRegistry.formulas() if formula.number[0] == 2}

    # --- assert -----------------------
    assert {param.values[0] for param in CANDIDATE_COUNTS} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_candidates", CANDIDATE_COUNTS)
def test_every_formula_gives_its_number_of_candidates_with_opposite_signs_at_the_bounds(formula_number, n_candidates):
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
