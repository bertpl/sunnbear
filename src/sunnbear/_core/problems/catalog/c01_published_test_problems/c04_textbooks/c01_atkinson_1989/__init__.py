"""This category holds the formulas of Atkinson (1989)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_equation_2_1_2,
    f02_equation_1_3_6,
    f03_equation_2_7_3,
    f04_case_1,
    f05_case_2,
    f06_case_3,
    f07_case_4,
    f08_problem_38_a,
)


class Atkinson1989(FormulaCategory):
    """`Atkinson1989` is the category of the formulas of 1 publication."""

    number = (1, 4, 1)
    name = "Atkinson (1989)"
    description = (
        "The test problems come from chapter 2, on rootfinding, of the textbook An Introduction to Numerical Analysis."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
