"""This category holds the formulas of Epperson (2013)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_example_3_1,
    f02_exercise_3_1_1,
    f03_exercise_3_1_2_b,
    f04_exercise_3_1_2_d,
    f05_exercise_3_1_2_e,
    f06_exercise_3_1_3_f,
    f07_exercise_3_1_3_g,
    f08_exercise_3_1_3_h,
    f09_exercise_3_1_13,
    f10_exercise_3_1_14_a,
    f11_exercise_3_1_14_b,
    f12_figure_3_2,
    f13_figure_3_8,
    f14_figure_3_3,
    f15_table_3_3,
    f16_exercise_3_5_6,
    f17_exercise_3_5_8,
    f18_example_3_8,
    f19_exercise_3_9_4,
    f20_exercise_3_9_8,
    f21_example_3_10,
    f22_figure_3_12,
    f23_exercise_3_11_25,
)


class Epperson2013(FormulaCategory):
    """`Epperson2013` is the category of the formulas of 1 publication."""

    number = (1, 4, 5)
    name = "Epperson (2013)"
    description = (
        "The test problems come from chapter 3, on root-finding, of the textbook An Introduction to"
        " Numerical Methods and Analysis."
    )
    publication = Publication(
        citation=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. John Wiley &"
            " Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        citation_key="Epperson13",
        authors=("Epperson, J. F.",),
        year=2013,
        title="An Introduction to Numerical Methods and Analysis",
        published_in="John Wiley & Sons",
    )
