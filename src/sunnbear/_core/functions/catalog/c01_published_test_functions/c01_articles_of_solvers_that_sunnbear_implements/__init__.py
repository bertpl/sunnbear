"""This category holds the formulas of articles of solvers that sunnbear implements, 1 category per source.

A script generates this file from the survey of published test problems.
"""

from sunnbear._core.functions.core import FormulaCategory

from . import c01_dowell_jarratt_1971


class ArticlesOfSolversThatSunnbearImplements(FormulaCategory):
    """`ArticlesOfSolversThatSunnbearImplements` is subcategory 1.1 of the published test functions."""

    number = (1, 1)
    name = "Articles of solvers that sunnbear implements"
