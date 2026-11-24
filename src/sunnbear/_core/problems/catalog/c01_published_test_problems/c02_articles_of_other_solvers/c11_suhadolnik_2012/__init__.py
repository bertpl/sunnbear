"""This category holds the formulas of Suhadolnik (2012)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_2,
    f02_function_4,
    f03_function_5,
    f04_function_7,
    f05_function_8,
    f06_function_9,
    f07_function_10,
    f08_function_11,
    f09_function_12,
    f10_function_13,
    f11_function_14,
    f12_function_15,
    f13_function_17,
    f14_function_18,
)


class Suhadolnik2012(FormulaCategory):
    """`Suhadolnik2012` is the category of the formulas of 1 publication."""

    number = (1, 2, 11)
    name = "Suhadolnik (2012)"
    description = "The test problems come from the article that introduces combined bracketing methods."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
