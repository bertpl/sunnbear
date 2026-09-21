"""This module re-exports the test-function framework: formulas, recipes, identities, and the registry.

How the pieces tie together is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    CandidateTestFunction,
    DecimalParamValue,
    ExponentialParamValue,
    Formula,
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
    "CandidateTestFunction",
    "DecimalParamValue",
    "ExponentialParamValue",
    "Formula",
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
