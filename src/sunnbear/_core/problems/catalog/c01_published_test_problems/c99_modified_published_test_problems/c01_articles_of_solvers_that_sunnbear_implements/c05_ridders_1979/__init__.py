"""This category holds the modified versions of the formulas of Ridders (1979)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_iii_2


class ModifiedRidders1979(FormulaCategory):
    """`ModifiedRidders1979` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.5, `Ridders1979`, and come from its publication.
    """

    number = (1, 99, 1, 5)
    name = "Ridders (1979)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces Ridders' method."
    )
