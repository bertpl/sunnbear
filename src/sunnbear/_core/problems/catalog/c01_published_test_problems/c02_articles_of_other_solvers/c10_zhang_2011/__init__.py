"""This category holds the formulas of Zhang (2011)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_3


class Zhang2011(FormulaCategory):
    """`Zhang2011` is the category of the formulas of 1 publication."""

    number = (1, 2, 10)
    name = "Zhang (2011)"
    description = "The test problems come from the article that introduces an improvement to Brent's method."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
