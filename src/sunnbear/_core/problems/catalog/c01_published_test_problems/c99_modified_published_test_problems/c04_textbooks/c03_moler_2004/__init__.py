"""This category holds the modified versions of the formulas of Moler (2004)."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_section_1_1,
    f02_section_1_7,
    f05_section_4_8,
    f06_section_4_10,
    f13_function_5,
    f14_exercise_4_3,
    f15_exercise_4_10_c,
)


class ModifiedMoler2004(FormulaCategory):
    """`ModifiedMoler2004` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.3, `Moler2004`, and come from the publication of `Moler2004`.
    """

    number = (1, 99, 4, 3)
    name = "Moler (2004)"
    description = (
        "The test problems are modified versions of those that come from the textbook Numerical Computing "
        "with MATLAB: from chapter 4, on zeros and roots, and from 2 examples of chapter 1."
    )
