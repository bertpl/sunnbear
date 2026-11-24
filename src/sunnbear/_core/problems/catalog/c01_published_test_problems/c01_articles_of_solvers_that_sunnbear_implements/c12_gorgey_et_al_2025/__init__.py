"""This category holds the formulas of Gorgey et al. (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_1, f02_equation_2, f03_equation_3, f04_equation_4, f05_equation_5


class GorgeyEtAl2025(FormulaCategory):
    """`GorgeyEtAl2025` is the category of the formulas of 1 publication."""

    number = (1, 1, 12)
    name = "Gorgey et al. (2025)"
    description = (
        "The test problems come from an article on the efficiency of a Scilab implementation of Ridders' method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
