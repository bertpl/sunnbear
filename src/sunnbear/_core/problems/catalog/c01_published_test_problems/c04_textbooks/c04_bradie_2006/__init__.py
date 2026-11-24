"""This category holds the formulas of Bradie (2006)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_2_page_55,
    f02_section_2_page_58,
    f03_section_2_1_page_59,
    f04_figure_2_2,
    f05_function_2,
    f06_example_2_2,
    f07_section_2_1_page_67,
    f08_exercise_2_1_1_a,
    f09_exercise_2_1_1_b,
    f10_exercise_2_1_1_c,
    f11_exercise_2_1_1_d,
    f12_exercise_2_1_2,
    f13_exercise_2_1_3,
    f14_exercise_2_1_4,
    f15_exercise_2_1_5,
    f16_exercise_2_1_11,
    f17_exercise_2_1_12,
    f18_exercise_2_1_14,
    f19_exercise_2_1_16_a,
    f20_exercise_2_1_16_b,
    f21_exercise_2_1_16_c,
    f22_exercise_2_1_17,
    f23_exercise_2_2_5,
    f24_exercise_2_2_9,
    f25_exercise_2_3_11,
    f26_exercise_2_3_12,
    f27_exercise_2_3_13,
    f28_example_2_10,
)


class Bradie2006(FormulaCategory):
    """`Bradie2006` is the category of the formulas of 1 publication."""

    number = (1, 4, 4)
    name = "Bradie (2006)"
    description = (
        "The test problems come from chapter 2, on rootfinding, of the textbook A Friendly "
        "Introduction to Numerical Analysis."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
