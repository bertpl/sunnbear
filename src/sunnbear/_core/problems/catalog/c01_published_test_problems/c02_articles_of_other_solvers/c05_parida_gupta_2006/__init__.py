"""This category holds the formulas of Parida, Gupta (2006)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_example_1, f02_example_2, f03_example_4


class ParidaGupta2006(FormulaCategory):
    """`ParidaGupta2006` is the category of the formulas of 1 publication."""

    number = (1, 2, 5)
    name = "Parida, Gupta (2006)"
    description = "The test problems come from the article that introduces an improved regula falsi method."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
