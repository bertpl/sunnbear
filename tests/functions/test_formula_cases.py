"""Drive every registered formula through its declared `FormulaTestCase` list."""

import math

import pytest

from sunnbear.functions import FormulaRegistry
from sunnbear.functions._test_cases import BracketTestCase, InvalidTestCase, ValueTestCase

# every (formula, case) pair, with a stable unique id: formula number + case kind + within-formula index
_INDEXED = [(formula, i, case) for formula in FormulaRegistry.formulas() for i, case in enumerate(formula.cases)]
_CASES = [(formula, case) for formula, _, case in _INDEXED]
_IDS = [f"F{formula.number}:{type(case).__name__}:{i}" for formula, i, case in _INDEXED]


@pytest.mark.parametrize("formula, case", _CASES, ids=_IDS)
def test_formula_test_case(formula, case):
    # --- act / assert -----------------
    match case:
        case ValueTestCase(params=params, x=x, c=c, expected=expected, rtol=rtol, atol=atol):
            p = formula.param_dict_to_tuple(params)
            assert formula.is_param_tuple_valid(*p)
            assert math.isclose(formula.bind_xc_fun(p)(x, c), expected, rel_tol=rtol, abs_tol=atol)
        case InvalidTestCase(params=params):
            assert not formula.is_param_tuple_valid(*formula.param_dict_to_tuple(params))
        case BracketTestCase(params=params, expected=(lo, hi), rtol=rtol, atol=atol):
            got_lo, got_hi = formula.bracket(*formula.param_dict_to_tuple(params))
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
    missing = [type(formula).__name__ for formula in FormulaRegistry.formulas() if not formula.cases]

    # --- assert -----------------------
    assert not missing, f"formulas with no test cases: {missing}"
