"""This category holds the formulas of Chen, Li (2007)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_example_1, f02_example_2, f03_example_4


class ChenLi2007(FormulaCategory):
    """`ChenLi2007` is the category of the formulas of 1 publication."""

    number = (1, 2, 6)
    name = "Chen, Li (2007)"
    description = "The test problems come from the article that introduces an improved exponential regula falsi method."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
