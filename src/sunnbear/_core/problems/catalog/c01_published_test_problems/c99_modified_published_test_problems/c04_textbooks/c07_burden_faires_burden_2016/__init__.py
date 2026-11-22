"""This category holds the modified versions of the formulas of Burden, Faires, Burden (2016)."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f04_section_2_2_example_1,
    f09_exercise_2_1_1,
    f11_exercise_2_1_3,
    f19_exercise_2_1_8,
    f43_exercise_2_4_1_c,
    f47_exercise_2_4_2_c,
    f48_exercise_2_4_2_d,
)


class ModifiedBurdenFairesBurden2016(FormulaCategory):
    """`ModifiedBurdenFairesBurden2016` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.7, `BurdenFairesBurden2016`, and come from the publication of
    `BurdenFairesBurden2016`.
    """

    number = (1, 99, 4, 7)
    name = "Burden, Faires, Burden (2016)"
    description = (
        "The test problems are modified versions of those that come from chapter 2, on equations in 1 "
        "variable, of the textbook Numerical Analysis."
    )
