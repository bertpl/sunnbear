"""Drive every registered formula through its declared `FormulaTestCase` list."""

import math

import pytest

from sunnbear._core.functions.core.taxonomy import FormulaTaxonomyNode
from sunnbear._core.functions.core.test_cases import IntervalBoundsTestCase, InvalidTestCase, ValueTestCase
from sunnbear.functions import FormulaRegistry

# _INDEXED holds every (formula, test case) pair, and _IDS gives each pair a stable unique id
_INDEXED = [
    (formula, i, test_case) for formula in FormulaRegistry.formulas() for i, test_case in enumerate(formula.test_cases)
]
_TEST_CASES = [(formula, test_case) for formula, _, test_case in _INDEXED]
_IDS = [
    f"f{FormulaTaxonomyNode.format_number(formula.number)}:{type(test_case).__name__}:{i}"
    for formula, i, test_case in _INDEXED
]


@pytest.mark.parametrize("formula, test_case", _TEST_CASES, ids=_IDS)
def test_formula_test_case(formula, test_case):
    # --- act / assert -----------------
    match test_case:
        case ValueTestCase(params=params, x=x, c=c, expected=expected, rtol=rtol, atol=atol):
            p = formula.param_dict_to_tuple(params)
            assert formula.is_param_tuple_valid(*p)
            value = formula.bind_xc_fun(p)(x, c)
            if math.isnan(expected):
                assert math.isnan(value)
            else:
                assert math.isclose(value, expected, rel_tol=rtol, abs_tol=atol)
        case InvalidTestCase(params=params):
            assert not formula.is_param_tuple_valid(*formula.param_dict_to_tuple(params))
        case IntervalBoundsTestCase(params=params, expected=(lo, hi), rtol=rtol, atol=atol):
            got_lo, got_hi = formula.interval_bounds(*formula.param_dict_to_tuple(params))
            assert math.isclose(got_lo, lo, rel_tol=rtol, abs_tol=atol)
            assert math.isclose(got_hi, hi, rel_tol=rtol, abs_tol=atol)


def test_param_dict_to_tuple_rejects_unknown_params():
    # --- arrange ----------------------
    formula = FormulaRegistry.formulas()[0]

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="param_names"):
        formula.param_dict_to_tuple({"nope": 1.0})


def test_every_formula_defines_test_cases():
    # --- act --------------------------
    missing = [type(formula).__name__ for formula in FormulaRegistry.formulas() if not formula.test_cases]

    # --- assert -----------------------
    assert not missing, f"formulas with no test cases: {missing}"
