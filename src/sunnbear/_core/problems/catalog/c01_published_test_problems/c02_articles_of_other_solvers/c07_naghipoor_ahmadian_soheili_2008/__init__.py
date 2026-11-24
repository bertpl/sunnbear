"""This category holds the formulas of Naghipoor, Ahmadian, Soheili (2008)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_1, f02_equation_2, f03_equation_3, f04_equation_4, f05_equation_6


class NaghipoorAhmadianSoheili2008(FormulaCategory):
    """`NaghipoorAhmadianSoheili2008` is the category of the formulas of 1 publication."""

    number = (1, 2, 7)
    name = "Naghipoor, Ahmadian, Soheili (2008)"
    description = (
        "The test problems come from the article that introduces an improved regula falsi method for simple zeros."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
