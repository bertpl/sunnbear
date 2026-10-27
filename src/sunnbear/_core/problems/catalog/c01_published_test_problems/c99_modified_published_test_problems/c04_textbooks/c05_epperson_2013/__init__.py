"""This category holds the modified formulas of Epperson (2013)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f08_3_1_3_h, f14_3_2_p_99, f15_3_2_p_100, f20_3_9_8, f21_ex_3_10, f22_3_11_4, f23_3_11_25


class ModifiedEpperson2013(FormulaCategory):
    """`ModifiedEpperson2013` is the category of the modified formulas of 1 publication.

    Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. John Wiley & Sons, Hoboken,
    NJ. ISBN 978-1-118-36759-9.
    """

    number = (1, 99, 4, 5)
    name = "Epperson (2013)"
