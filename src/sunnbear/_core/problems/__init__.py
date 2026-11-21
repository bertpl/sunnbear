"""This package holds the test-problem layer: the framework in `core`, the shipped formulas in `catalog`.

Importing this package imports the catalog, so every shipped formula and category is registered with
`FormulaRegistry` (in `core`) as soon as this package is imported.
"""

from . import catalog
from .core import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    DEFAULT_MARKER_MACROS,
    USER_DEFINED_FORMULA_CATEGORY_NUMBER,
    CandidateTestProblem,
    EffectOfC,
    Formula,
    FormulaCategory,
    FormulaParam,
    FormulaPresentation,
    FormulaRegistry,
    FormulaSource,
    FormulaTestCase,
    LatexTemplate,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
    ParamTable,
    ProblemId,
    TestProblem,
    XCFun,
    XFun,
    deduplicate_param_tuples,
)
