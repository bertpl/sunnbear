"""Drive every registered formula through its declared `FormulaTestCase` list."""

import math

import pytest

from sunnbear.functions import FormulaRegistry
from sunnbear.functions._test_cases import BracketTestCase, DEFAULT_ATOL, InvalidTestCase, ValueTestCase

# every (formula, case) pair across the catalog, so one parametrized test drives them all
_CASES = [(formula, case) for formula in FormulaRegistry.formulas() for case in formula.cases]
_IDS = [f"F{formula.number}:{type(case).__name__}" for formula, case in _CASES]


@pytest.mark.parametrize("formula, case", _CASES, ids=_IDS)
def test_formula_test_case(formula, case):
    # --- act / assert -----------------
    match case:
        case ValueTestCase(params=p, x=x, c=c, expected=expected, rtol=rtol, atol=atol):
            assert formula.is_param_tuple_valid(*p)
            assert math.isclose(formula.bind_xc_fun(p)(x, c), expected, rel_tol=rtol, abs_tol=atol)
        case InvalidTestCase(params=p):
            assert not formula.is_param_tuple_valid(*p)
        case BracketTestCase(params=p, expected=(lo, hi)):
            got_lo, got_hi = formula.bracket(*p)
            assert math.isclose(got_lo, lo, abs_tol=DEFAULT_ATOL)
            assert math.isclose(got_hi, hi, abs_tol=DEFAULT_ATOL)


def test_every_formula_defines_test_cases():
    # --- act --------------------------
    missing = [type(formula).__name__ for formula in FormulaRegistry.formulas() if not formula.cases]

    # --- assert -----------------------
    assert not missing, f"formulas with no test cases: {missing}"
