"""This category holds the formulas of Ridders (1979)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_i, f02_function_1, f03_function_2, f04_function_3


class Ridders1979(FormulaCategory):
    """`Ridders1979` is the category of the formulas of 1 publication."""

    number = (1, 1, 5)
    name = "Ridders (1979)"
    description = "The test problems come from the article that introduces Ridders' method."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
