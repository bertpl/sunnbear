"""The simple polynomial formulas (category 2.1) give the expected candidates, with shared values at the bounds."""

import pytest

from sunnbear._core.problems.core import FormulaRegistry

# Each entry holds a simple polynomial formula's number, the number of values of its first parameter (a power ``p`` or a
# term count ``n``), the number of values of its second parameter (a weight ``w`` or a slope ``m``), and the bounds of
# its interval, at which its value at ``c = 0`` is half the interval's width, negative at the lower bound.
CANDIDATE_GRID_SIZES = [
    pytest.param((2, 1, 1), 1, 1, (-1.0, 1.0), id="linear"),
    pytest.param((2, 1, 2), 5, 31, (-1.0, 1.0), id="linear_plus_even_power"),
    pytest.param((2, 1, 3), 4, 43, (-1.0, 1.0), id="linear_plus_odd_power"),
    pytest.param((2, 1, 4), 4, 31, (-1.0, 1.0), id="linear_plus_sum_of_even_powers"),
    pytest.param((2, 1, 5), 3, 43, (-1.0, 1.0), id="linear_plus_sum_of_odd_powers"),
    pytest.param((2, 1, 6), 9, 25, (0.0, 1.0), id="one_sided_linear_plus_power"),
]


def test_the_parametrization_names_every_simple_polynomial_formula():
    """`CANDIDATE_GRID_SIZES` names exactly the formulas of category 2.1."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 1)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in CANDIDATE_GRID_SIZES} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_first_param_values, n_second_param_values, interval", CANDIDATE_GRID_SIZES)
def test_every_candidate_passes_through_the_same_points_at_the_bounds(
    formula_number, n_first_param_values, n_second_param_values, interval
):
    """Each formula combines every power or term count with every value of its other parameter, and at ``c = 0`` every
    candidate of a formula has the same values at the bounds of its interval."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_first_param_values * n_second_param_values
    a, b = interval
    half_width = (b - a) / 2
    for candidate in candidates:
        assert (candidate.a, candidate.b) == (a, b)
        assert candidate.xc_fun(a, 0.0) == pytest.approx(-half_width, abs=1e-12)
        assert candidate.xc_fun(b, 0.0) == pytest.approx(half_width, abs=1e-12)


@pytest.mark.parametrize("formula_number", [(2, 1, 3), (2, 1, 5)])
def test_the_positive_and_the_negative_slopes_have_the_same_sizes(formula_number):
    """The slopes ``m`` of a formula hold 21 positive values from 0.001 to 10, their negatives, and 0, and every power
    or term count gets all of them."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    slopes_per_first_param: dict[float, list[float]] = {}
    for candidate in formula.build_all_candidates():
        first_param, m = candidate.id.param_values
        slopes_per_first_param.setdefault(first_param, []).append(m)

    # --- assert -----------------------
    for slopes in slopes_per_first_param.values():
        positive_slopes = sorted(m for m in slopes if m > 0.0)
        negative_slopes = sorted(m for m in slopes if m < 0.0)
        assert (positive_slopes[0], positive_slopes[-1], len(positive_slopes)) == (0.001, 10.0, 21)
        assert sorted(-m for m in negative_slopes) == positive_slopes
        assert slopes.count(0.0) == 1
        assert len(slopes) == 43
