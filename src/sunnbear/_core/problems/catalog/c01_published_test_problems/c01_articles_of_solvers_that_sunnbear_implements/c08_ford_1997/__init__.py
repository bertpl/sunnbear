"""This category holds the formulas of Ford (1997)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_1, f02_function_2, f03_function_3, f04_function_4, f05_function_5


class Ford1997(FormulaCategory):
    """`Ford1997` is the category of the formulas of 1 publication."""

    number = (1, 1, 8)
    name = "Ford (1997)"
    description = "The test problems come from the article that introduces improved Illinois-type methods."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
