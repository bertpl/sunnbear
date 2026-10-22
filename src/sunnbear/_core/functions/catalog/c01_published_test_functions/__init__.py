"""This category holds the test functions of published sources, grouped by kind of source, then by source."""

from sunnbear._core.functions.core import FormulaCategory

from . import (
    c01_articles_of_solvers_that_sunnbear_implements,
    c02_articles_of_other_solvers,
    c03_public_benchmark_suites,
    c04_textbooks,
)


class PublishedTestFunctions(FormulaCategory):
    """`PublishedTestFunctions` is the top-level category of formulas taken from published sources."""

    number = (1,)
    name = "Published test functions"
    is_builtin_only = True
