"""This category holds the formulas of Ellithy (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_problem_1,
    f02_problem_16,
    f03_problem_17,
    f04_problem_19,
    f05_problem_20,
    f06_problem_21,
    f07_problem_22,
    f08_problem_23,
    f09_problem_24,
    f10_problem_25,
    f11_problem_26,
    f12_problem_27,
    f13_problem_29,
    f14_problem_30,
    f15_problem_32,
    f16_problem_33,
    f17_problem_34,
    f18_problem_35,
    f19_problem_36,
    f20_problem_38,
    f21_problem_40,
    f22_problem_41,
    f23_problem_42,
    f24_problem_43,
    f25_problem_45,
    f26_problem_46,
    f27_problem_47,
    f28_problem_48,
)


class Ellithy2026(FormulaCategory):
    """`Ellithy2026` is the category of the formulas of 1 publication."""

    number = (1, 2, 18)
    name = "Ellithy (2026)"
    description = (
        "The test problems come from the data set of the article that introduces 4 multi-phase "
        "hybrid bracketing methods."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
