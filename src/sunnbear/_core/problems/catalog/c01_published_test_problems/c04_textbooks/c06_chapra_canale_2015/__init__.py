"""This category holds the formulas of Chapra, Canale (2015)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_equation_pt2_3,
    f02_example_5_2,
    f03_figure_5_14,
    f04_figure_7_6,
    f05_figure_7_8,
    f06_equation_8_14,
    f07_figure_8_4,
    f08_figure_8_5,
    f09_figure_8_6,
    f10_problem_5_1,
    f11_problem_5_2,
    f12_problem_5_3,
    f13_problem_5_4,
    f14_problem_5_5,
    f15_problem_5_6,
    f16_problem_5_7,
    f17_problem_5_8,
    f18_problem_5_10,
    f19_problem_5_11,
    f20_problem_5_15,
    f21_problem_5_16,
    f22_problem_5_17,
    f23_problem_5_18,
    f24_problem_6_13,
    f25_problem_6_17,
    f26_problem_8_5,
    f27_problem_8_15,
    f28_problem_8_33,
    f29_problem_8_39,
)


class ChapraCanale2015(FormulaCategory):
    """`ChapraCanale2015` is the category of the formulas of 1 publication."""

    number = (1, 4, 6)
    name = "Chapra, Canale (2015)"
    description = (
        "The test problems come from Part Two, on roots of equations, of the textbook Numerical Methods for Engineers."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
