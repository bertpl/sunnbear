"""This category holds the modified versions of the formulas of Epperson (2013)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f08_3_1_3_h, f11_3_1_14_b, f14_3_2_p_99, f15_3_2_p_100, f20_3_9_8, f21_ex_3_10, f22_3_11_4, f23_3_11_25


class ModifiedEpperson2013(FormulaCategory):
    """`ModifiedEpperson2013` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.5, `Epperson2013`, and come from its publication.
    """

    number = (1, 99, 4, 5)
    name = "Epperson (2013)"
    description = (
        "The test problems are modified versions of those that come from chapter 3, on root-finding, of the "
        "textbook An Introduction to Numerical Methods and Analysis."
    )
