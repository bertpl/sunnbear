"""This category holds the formulas of Brent (1973)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_row_1, f02_row_3, f03_equation_4_1, f04_equation_4_2


class Brent1973(FormulaCategory):
    """`Brent1973` is the category of the formulas of 1 publication."""

    number = (1, 1, 4)
    name = "Brent (1973)"
    description = (
        "The test problems come from chapter 4 of the book Algorithms for Minimization without "
        "Derivatives, which presents Brent's method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
