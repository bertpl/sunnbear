"""This category holds the formulas of textbooks, in 1 subcategory per source.

A script generates this file from the survey of published test problems: to change it, change the survey and run
`scripts/literature_test_problems/formula_modules.py`, never this file.
"""

from sunnbear._core.functions.core import FormulaCategory


class Textbooks(FormulaCategory):
    """`Textbooks` is subcategory 1.4 of the published test functions."""

    number = (1, 4)
    name = "Textbooks"
