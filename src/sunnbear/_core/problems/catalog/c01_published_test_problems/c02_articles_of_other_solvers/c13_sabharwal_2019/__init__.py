"""This category holds the formulas of Sabharwal (2019)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_figure_1,
    f02_figure_2,
    f03_figure_3,
    f04_figure_4,
    f05_function_1,
    f06_function_4,
    f07_function_5,
    f08_function_6,
    f09_function_8,
    f10_function_10,
    f11_function_11,
)


class Sabharwal2019(FormulaCategory):
    """`Sabharwal2019` is the category of the formulas of 1 publication."""

    number = (1, 2, 13)
    name = "Sabharwal (2019)"
    description = "The test problems come from the article that introduces a hybrid of bisection and regula falsi."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
