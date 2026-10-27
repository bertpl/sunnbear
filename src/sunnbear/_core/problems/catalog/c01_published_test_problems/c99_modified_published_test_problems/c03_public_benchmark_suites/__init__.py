"""This category holds the modified versions of the formulas of public benchmark suites."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_burkardt_2016,
    c02_gsl_2024,
    c03_roots_fortran_2025,
    c04_ganchovski_2026,
    c05_borchers_2026,
    c06_roots_jl_2026,
)


class ModifiedPublicBenchmarkSuites(FormulaCategory):
    """`ModifiedPublicBenchmarkSuites` is subcategory 1.99.3.

    It holds the modified versions of the formulas of subcategory 1.3.
    """

    number = (1, 99, 3)
    name = "Public benchmark suites"
