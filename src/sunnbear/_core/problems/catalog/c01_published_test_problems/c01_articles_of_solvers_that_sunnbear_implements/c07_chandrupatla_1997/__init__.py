"""This category holds the formulas of Chandrupatla (1997)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_1,
    f02_function_2,
    f03_function_3,
    f04_function_4,
    f05_function_5,
    f06_function_6,
    f07_function_7,
    f08_function_8,
    f09_function_9,
)


class Chandrupatla1997(FormulaCategory):
    """`Chandrupatla1997` is the category of the formulas of 1 publication."""

    number = (1, 1, 7)
    name = "Chandrupatla (1997)"
    description = (
        "The test problems come from the article that introduces Chandrupatla's method, a hybrid of"
        " quadratic interpolation and bisection."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
