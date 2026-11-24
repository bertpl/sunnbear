"""This category holds the formulas of Galdino (2011)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_f1,
    f02_function_f2,
    f03_function_f3,
    f04_function_f4,
    f05_function_f5,
    f06_function_f6,
    f07_function_f7,
)


class Galdino2011(FormulaCategory):
    """`Galdino2011` is the category of the formulas of 1 publication."""

    number = (1, 2, 9)
    name = "Galdino (2011)"
    description = "The test problems come from the article that introduces a family of regula falsi methods."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
