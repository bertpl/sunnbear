"""This category holds the modified versions of the formulas of Epperson (2013)."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f08_exercise_3_1_3_h,
    f11_exercise_3_1_14_b,
    f14_figure_3_3,
    f15_table_3_3,
    f20_exercise_3_9_8,
    f21_example_3_10,
    f22_figure_3_12,
    f23_exercise_3_11_25,
)


class ModifiedEpperson2013(FormulaCategory):
    """`ModifiedEpperson2013` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.5, `Epperson2013`, and come from the publication of `Epperson2013`.
    """

    number = (1, 99, 4, 5)
    name = "Epperson (2013)"
    description = (
        "The test problems are modified versions of those that come from chapter 3, on root-finding, of the "
        "textbook An Introduction to Numerical Methods and Analysis."
    )
