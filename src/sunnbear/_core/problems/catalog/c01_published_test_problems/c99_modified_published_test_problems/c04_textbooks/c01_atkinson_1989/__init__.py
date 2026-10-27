"""This category holds the modified versions of the formulas of Atkinson (1989)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_1_3_6, f06_2_8_case_3, f07_2_8_case_4, f08_p38_a


class ModifiedAtkinson1989(FormulaCategory):
    """`ModifiedAtkinson1989` holds the modified versions of the formulas of 1 publication.

    Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & Sons, New York. ISBN
    0-471-62489-6.
    """

    number = (1, 99, 4, 1)
    name = "Atkinson (1989)"
