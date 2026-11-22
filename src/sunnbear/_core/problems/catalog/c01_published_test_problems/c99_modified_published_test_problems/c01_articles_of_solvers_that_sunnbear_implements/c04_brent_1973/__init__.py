"""This category holds the modified versions of the formulas of Brent (1973)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_4_1


class ModifiedBrent1973(FormulaCategory):
    """`ModifiedBrent1973` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.4, `Brent1973`, and come from its publication.
    """

    number = (1, 99, 1, 4)
    name = "Brent (1973)"
    description = (
        "The test problems are modified versions of those that come from chapter 4 of the book Algorithms for "
        "Minimization without Derivatives, which presents Brent's method."
    )
