"""This category holds the test functions of published sources, grouped by kind of source, then by source."""

from sunnbear._core.functions.core import FormulaCategory


class PublishedTestFunctions(FormulaCategory):
    """`PublishedTestFunctions` is the top-level category of formulas taken from published sources."""

    number = (1,)
    name = "Published test functions"
    is_builtin_only = True
