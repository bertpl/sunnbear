"""Category 1 holds formulas taken from existing benchmark suites, grouped by source, then by suite."""

from sunnbear._core.functions.core import FormulaCategory


class ExistingBenchmarkSuites(FormulaCategory):
    """`ExistingBenchmarkSuites` is the top-level category of formulas taken from existing benchmark suites."""

    number = (1,)
    name = "Existing benchmark suites"
    is_builtin_only = True
