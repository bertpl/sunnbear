"""The polynomial formulas (category 2.1) give the expected candidates, which share their values at the bounds."""

import pytest

from sunnbear._core.problems.core import FormulaRegistry

# Each entry holds a polynomial formula's number, the number of values of its first parameter (a power ``p`` or a
# term count ``n``), and the number of values of its second parameter (a weight ``w`` or a slope ``m``).
CANDIDATE_GRID_SIZES = [
    pytest.param((2, 1, 1), 1, 1, id="linear"),
    pytest.param((2, 1, 2), 5, 41, id="linear_plus_even_power"),
    pytest.param((2, 1, 3), 4, 42, id="linear_plus_odd_power"),
    pytest.param((2, 1, 4), 4, 41, id="linear_plus_sum_of_even_first_param_values"),
    pytest.param((2, 1, 5), 3, 42, id="linear_plus_sum_of_odd_powers"),
]


def test_the_parametrization_names_every_polynomial_formula():
    """`CANDIDATE_GRID_SIZES` names exactly the formulas of category 2.1."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 1)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in CANDIDATE_GRID_SIZES} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_first_param_values, n_second_param_values", CANDIDATE_GRID_SIZES)
def test_every_candidate_passes_through_the_same_points_at_the_bounds(
    formula_number, n_first_param_values, n_second_param_values
):
    """Each formula combines every power or term count with every value of its other parameter, and at ``c = 0`` every
    candidate passes through ``(-1, -1)`` and ``(1, 1)``, the bounds of its interval."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_first_param_values * n_second_param_values
    for candidate in candidates:
        assert (candidate.a, candidate.b) == (-1.0, 1.0)
        assert candidate.xc_fun(-1.0, 0.0) == pytest.approx(-1.0, abs=1e-12)
        assert candidate.xc_fun(1.0, 0.0) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("formula_number", [(2, 1, 3), (2, 1, 5)])
def test_the_slopes_run_from_the_negative_ones_through_0_to_just_below_1(formula_number):
    """The slopes ``m`` of a formula hold 21 negative values from -10 to -0.1, then 0, then 20 values from 0.01 to
    ``10^-0.1``, and every power or term count gets all of them."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    slopes_per_first_param: dict[float, list[float]] = {}
    for candidate in formula.build_all_candidates():
        first_param, m = candidate.id.param_values
        slopes_per_first_param.setdefault(first_param, []).append(m)

    # --- assert -----------------------
    for slopes in slopes_per_first_param.values():
        sorted_slopes = sorted(slopes)
        assert (sorted_slopes[0], sorted_slopes[20], sorted_slopes[21]) == (-10.0, -0.1, 0.0)
        assert (sorted_slopes[22], sorted_slopes[-1]) == (0.01, pytest.approx(10**-0.1))
        assert len(slopes) == 42
