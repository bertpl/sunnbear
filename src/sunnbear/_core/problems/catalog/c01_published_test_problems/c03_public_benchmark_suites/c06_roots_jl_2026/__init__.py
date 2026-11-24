"""This category holds the formulas of Roots.jl (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_func2,
    f02_function_func9,
    f03_function_func10,
    f04_function_func11,
    f05_function_f2,
    f06_function_f4,
    f07_function_f5,
    f08_function_f8,
    f09_function_f9,
)


class RootsJl2026(FormulaCategory):
    """`RootsJl2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 6)
    name = "Roots.jl (2026)"
    description = "The test problems come from the tests of Roots.jl, a Julia package of root finders, version 3.0.11."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
