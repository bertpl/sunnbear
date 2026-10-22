"""This category holds the formulas of articles of solvers that sunnbear implements, in 1 subcategory per source.

A script generates this file from the survey of published test problems: to change it, change the survey and run
`scripts/literature_test_problems/formula_modules.py`, never this file.
"""

from sunnbear._core.functions.core import FormulaCategory

from . import c01_dowell_jarratt_1971


class ArticlesOfSolversThatSunnbearImplements(FormulaCategory):
    """`ArticlesOfSolversThatSunnbearImplements` is subcategory 1.1 of the published test functions."""

    number = (1, 1)
    name = "Articles of solvers that sunnbear implements"
