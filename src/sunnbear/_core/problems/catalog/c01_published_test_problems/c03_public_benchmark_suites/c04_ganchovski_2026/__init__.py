"""This category holds the formulas of Ganchovski (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_f93, f02_function_f100, f03_function_f101


class Ganchovski2026(FormulaCategory):
    """`Ganchovski2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 4)
    name = "Ganchovski (2026)"
    description = (
        "The test problems come from Root-finding Test Functions, the collection of functions in "
        "the repository of the modified Anderson–Björck method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
