"""Formulas taken from existing benchmark suites (category 1), grouped by source, then by suite."""

from sunnbear._core.functions.core import FormulaCategory


class ExistingBenchmarkSuites(FormulaCategory):
    """Top-level category of the formulas taken from existing benchmark suites."""

    number = (1,)
    name = "Existing benchmark suites"
    is_builtin_only = True
