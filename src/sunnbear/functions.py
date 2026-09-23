"""This module re-exports the test-function framework: formulas, categories, recipes, identities, and the registry.

How the pieces tie together is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    USER_DEFINED_FORMULA_CATEGORY_NUMBER,
    CandidateTestFunction,
    DecimalParamValue,
    ExponentialParamValue,
    Formula,
    FormulaCategory,
    FormulaRegistry,
    FormulaTestCase,
    FunctionId,
    ParamAxis,
    ParamNotation,
    ParamRecipe,
    ParamValue,
    TestFunction,
    XCFun,
    XFun,
    deduplicate_param_tuples,
)

__all__ = [
    "CANONICAL_DIGITS",
    "DEDUP_DIGITS",
    "USER_DEFINED_FORMULA_CATEGORY_NUMBER",
    "CandidateTestFunction",
    "DecimalParamValue",
    "ExponentialParamValue",
    "Formula",
    "FormulaCategory",
    "FormulaRegistry",
    "FormulaTestCase",
    "FunctionId",
    "ParamAxis",
    "ParamNotation",
    "ParamRecipe",
    "ParamValue",
    "TestFunction",
    "XCFun",
    "XFun",
    "deduplicate_param_tuples",
]
