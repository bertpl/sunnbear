"""This category holds the formulas of Gottlieb, Thompson (2010)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_test_1, f02_test_3, f03_test_7


class GottliebThompson2010(FormulaCategory):
    """`GottliebThompson2010` is the category of the formulas of 1 publication."""

    number = (1, 2, 8)
    name = "Gottlieb, Thompson (2010)"
    description = (
        "The test problems come from the article that introduces the bisected direct quadratic regula falsi method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
