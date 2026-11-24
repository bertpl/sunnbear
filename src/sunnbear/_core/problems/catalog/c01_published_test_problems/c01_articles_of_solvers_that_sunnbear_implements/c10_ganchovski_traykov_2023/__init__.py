"""This category holds the formulas of Ganchovski, Traykov (2023)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_3


class GanchovskiTraykov2023(FormulaCategory):
    """`GanchovskiTraykov2023` is the category of the formulas of 1 publication."""

    number = (1, 1, 10)
    name = "Ganchovski, Traykov (2023)"
    description = (
        "The test problems come from the article that introduces the modified Anderson–Björck "
        "method, for nonlinear equations in structural mechanics."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
