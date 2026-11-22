"""This category holds the modified versions of the formulas of Moler (2004)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1_1, f02_1_7, f05_4_7_4_8, f06_4_7_4_10, f13_ex_4_1_5, f14_ex_4_3, f15_ex_4_10_c


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
