"""This package holds the test-function layer: the framework in `core`, the shipped formulas in `catalog`.

Importing this package imports the catalog, so every shipped formula is registered before
`FormulaRegistry` (in `core`) is first read.
"""

from . import catalog
from .core import (
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
