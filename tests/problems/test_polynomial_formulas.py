"""The polynomial formulas (category 2.1) give the expected candidates, which share their values at the bounds."""

import pytest

from sunnbear._core.problems.core import FormulaRegistry


@pytest.mark.parametrize(
    "formula_number, n_powers, n_values_per_power",
    [
        pytest.param((2, 1, 1), 1, 1, id="linear"),
        pytest.param((2, 1, 2), 5, 41, id="linear_plus_even_power"),
        pytest.param((2, 1, 3), 4, 42, id="linear_plus_odd_power"),
        pytest.param((2, 1, 4), 4, 41, id="linear_plus_sum_of_even_powers"),
        pytest.param((2, 1, 5), 3, 42, id="linear_plus_sum_of_odd_powers"),
    ],
)
def test_every_candidate_passes_through_the_same_points_at_the_bounds(formula_number, n_powers, n_values_per_power):
    """Each formula combines every power with every value of its other parameter, and at ``c = 0`` every candidate
    passes through ``(-1, -1)`` and ``(1, 1)``, the bounds of its interval."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_powers * n_values_per_power
    for candidate in candidates:
        assert (candidate.a, candidate.b) == (-1.0, 1.0)
        assert candidate.xc_fun(-1.0, 0.0) == pytest.approx(-1.0, abs=1e-12)
        assert candidate.xc_fun(1.0, 0.0) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("formula_number", [(2, 1, 3), (2, 1, 5)])
def test_the_slopes_run_from_the_negative_ones_through_0_to_just_below_1(formula_number):
    """The slopes ``s`` of a formula hold 21 negative values from -10 to -0.1, then 0, then 20 values from 0.01 to
    ``10^-0.1``, and every power gets all of them."""
    # --- arrange ----------------------
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == formula_number]

    # --- act --------------------------
    slopes_per_power: dict[float, list[float]] = {}
    for candidate in formula.build_all_candidates():
        n, s = candidate.id.param_values
        slopes_per_power.setdefault(n, []).append(s)

    # --- assert -----------------------
    for slopes in slopes_per_power.values():
        sorted_slopes = sorted(slopes)
        assert (sorted_slopes[0], sorted_slopes[20], sorted_slopes[21]) == (-10.0, -0.1, 0.0)
        assert (sorted_slopes[22], sorted_slopes[-1]) == (0.01, pytest.approx(10**-0.1))
        assert len(slopes) == 42
