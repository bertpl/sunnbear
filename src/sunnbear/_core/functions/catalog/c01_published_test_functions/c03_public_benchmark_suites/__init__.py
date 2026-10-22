"""This category holds the formulas of public benchmark suites, 1 category per source.

A script generates this file from the survey of published test problems.
"""

from sunnbear._core.functions.core import FormulaCategory


class PublicBenchmarkSuites(FormulaCategory):
    """`PublicBenchmarkSuites` is subcategory 1.3 of the published test functions."""

    number = (1, 3)
    name = "Public benchmark suites"
