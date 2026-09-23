"""This package holds the test-function layer: the framework in `core`, the shipped formulas in `catalog`.

Importing this package imports the catalog, so every shipped formula and category is registered with
`FormulaRegistry` (in `core`) as soon as this package is imported.
"""

from . import catalog
from .core import (
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
