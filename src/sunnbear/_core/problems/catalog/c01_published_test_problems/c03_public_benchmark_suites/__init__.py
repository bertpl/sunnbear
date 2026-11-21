"""This category holds the formulas of public benchmark suites, in 1 subcategory per source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_burkardt_2016,
    c02_gsl_2024,
    c03_roots_fortran_2025,
    c04_ganchovski_2026,
    c05_borchers_2026,
    c06_roots_jl_2026,
    c07_scimlbenchmarks_jl_2026,
    c08_scipy_2026,
)


class PublicBenchmarkSuites(FormulaCategory):
    """`PublicBenchmarkSuites` is subcategory 1.3 of the published test problems."""

    number = (1, 3)
    name = "Public benchmark suites"
    description = (
        "The test problems come from public collections of test problems for root finders, such as the test "
        "suites of numerical libraries."
    )
