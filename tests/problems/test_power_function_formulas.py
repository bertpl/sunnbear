"""The power function formulas (category 2.3) give the expected candidates, each with a sign change over its interval.

The other tests cover what each formula adds to a plain power: the linear term of `SignedPower1`, the rule for the
interval ``[d, 1]``, and the finite values of `SignedReciprocalPower` at and next to its pole.
"""

import math

import pytest

from sunnbear._core.problems.catalog.c02_standard_function_families.c03_power_functions import (
    f05_signed_reciprocal_power,
)
from sunnbear._core.problems.core import Formula, FormulaRegistry

# Each entry holds a power function formula's number and its number of candidates.
#
# `NearEdgePower` has 81 candidates whose interval starts at the edge, and 63 whose interval starts near it.
# `NearPolePower` sweeps 81 powers at each of 6 distances, of which 63 pairs have no root inside the interval.
POWER_FUNCTION_FORMULAS = [
    pytest.param((2, 3, 1), 121, id="signed_power_1"),
    pytest.param((2, 3, 2), 121, id="signed_power_2"),
    pytest.param((2, 3, 3), 81 + 63, id="near_edge_power"),
    pytest.param((2, 3, 4), 81 * 6 - 63, id="near_pole_power"),
    pytest.param((2, 3, 5), 61, id="signed_reciprocal_power"),
]

MAX_ABS_VALUE = f05_signed_reciprocal_power.MAX_ABS_VALUE


def _formula(number: tuple[int, ...]) -> Formula:
    """Return the registered formula with `number`."""
    [formula] = [formula for formula in FormulaRegistry.formulas() if formula.number == number]
    return formula


def test_the_parametrization_names_every_power_function_formula():
    """`POWER_FUNCTION_FORMULAS` names exactly the formulas of category 2.3."""
    # --- act --------------------------
    formula_numbers_in_category = {
        formula.number for formula in FormulaRegistry.formulas() if formula.number[:2] == (2, 3)
    }

    # --- assert -----------------------
    assert {param.values[0] for param in POWER_FUNCTION_FORMULAS} == formula_numbers_in_category


@pytest.mark.parametrize("formula_number, n_candidates", POWER_FUNCTION_FORMULAS)
def test_every_candidate_has_opposite_signs_at_the_bounds_of_its_interval(formula_number, n_candidates):
    """A formula gives its expected number of candidates, each negative at its lower or upper bound and positive at
    the other, at ``c = 0``."""
    # --- arrange ----------------------
    formula = _formula(formula_number)

    # --- act --------------------------
    candidates = formula.build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == n_candidates
    for candidate in candidates:
        value_at_a, value_at_b = candidate.xc_fun(candidate.a, 0.0), candidate.xc_fun(candidate.b, 0.0)
        assert min(value_at_a, value_at_b) < 0.0 < max(value_at_a, value_at_b), candidate.id


@pytest.mark.parametrize("c", [0.3, -0.7])
def test_signed_power_1_is_exactly_0_only_at_its_root(c):
    """At every power, `SignedPower1` is 0 at its root and has the sign of ``z`` at the floats next to it, also where
    the power itself underflows to 0.

    Both values of ``c`` put the root away from 0. Next to a root at 0 the floats lie so close together that the
    linear term underflows too.
    """
    # --- arrange ----------------------
    candidates = _formula((2, 3, 1)).build_all_candidates()

    # --- act / assert -----------------
    for candidate in candidates:
        [p] = candidate.id.param_values
        root = c / (1.0 + p)
        assert candidate.xc_fun(root, c) == 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(root, -math.inf), c) < 0.0, candidate.id
        assert candidate.xc_fun(math.nextafter(root, math.inf), c) > 0.0, candidate.id


def test_near_edge_power_and_near_pole_power_keep_the_same_pairs_of_power_and_distance():
    """Among the powers that both formulas sweep at a distance above 0, both keep the same pairs ``(p, d)``."""
    # --- arrange ----------------------
    near_edge_candidates = _formula((2, 3, 3)).build_all_candidates()
    near_pole_candidates = _formula((2, 3, 4)).build_all_candidates()

    # --- act --------------------------
    near_edge_pairs = {candidate.id.param_values for candidate in near_edge_candidates if candidate.a > 0.0}
    highest_shared_power = max(p for p, d in near_edge_pairs)
    near_pole_pairs = {
        candidate.id.param_values
        for candidate in near_pole_candidates
        if candidate.id.param_values[0] <= highest_shared_power
    }

    # --- assert -----------------------
    assert len(near_edge_pairs) == 63
    assert near_edge_pairs == near_pole_pairs


@pytest.mark.parametrize("c", [0.0, 0.3, -0.7])
def test_signed_reciprocal_power_is_finite_at_and_next_to_its_pole(c):
    """At every power, `SignedReciprocalPower` is 0 at its pole, and at the floats next to the pole it has the sign of
    ``z`` and a size of at most `MAX_ABS_VALUE`."""
    # --- arrange ----------------------
    candidates = _formula((2, 3, 5)).build_all_candidates()

    # --- act / assert -----------------
    for candidate in candidates:
        [p] = candidate.id.param_values
        pole = c / (1.0 + p)
        value_below = candidate.xc_fun(math.nextafter(pole, -math.inf), c)
        value_above = candidate.xc_fun(math.nextafter(pole, math.inf), c)
        assert candidate.xc_fun(pole, c) == 0.0, candidate.id
        assert -MAX_ABS_VALUE <= value_below < 0.0, candidate.id
        assert 0.0 < value_above <= MAX_ABS_VALUE, candidate.id
