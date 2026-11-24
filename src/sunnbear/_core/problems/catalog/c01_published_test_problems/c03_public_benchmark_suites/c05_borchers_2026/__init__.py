"""This category holds the formulas of Borchers (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_f1,
    f02_function_f2,
    f03_function_f3,
    f04_function_f4,
    f05_function_f5,
    f06_function_f6,
    f07_function_f7,
    f08_function_f8,
    f09_function_f9,
    f10_function_f10,
    f11_function_f11,
    f12_function_f12,
    f13_section_5_2_2,
)


class Borchers2026(FormulaCategory):
    """`Borchers2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 5)
    name = "Borchers (2026)"
    description = (
        "The test problems come from the chapter on root finding of the pracma Handbook, which "
        "documents the R package pracma."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
