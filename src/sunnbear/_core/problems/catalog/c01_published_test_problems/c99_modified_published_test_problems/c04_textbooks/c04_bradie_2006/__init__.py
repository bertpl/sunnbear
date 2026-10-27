"""This category holds the modified versions of the formulas of Bradie (2006)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f06_ex_2_2, f28_ex_2_10


class ModifiedBradie2006(FormulaCategory):
    """`ModifiedBradie2006` holds the modified versions of the formulas of 1 publication.

    Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, Upper Saddle River, NJ.
    ISBN 0-13-013054-0.
    """

    number = (1, 99, 4, 4)
    name = "Bradie (2006)"
