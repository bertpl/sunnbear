"""This category holds the modified versions of the formulas of Bradie (2006)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f06_ex_2_2, f07_2_1_p_67, f28_ex_2_10


class ModifiedBradie2006(FormulaCategory):
    """`ModifiedBradie2006` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.4, `Bradie2006`, and come from the publication of `Bradie2006`.
    """

    number = (1, 99, 4, 4)
    name = "Bradie (2006)"
    description = (
        "The test problems are modified versions of those that come from chapter 2, on rootfinding, of the "
        "textbook A Friendly Introduction to Numerical Analysis."
    )
