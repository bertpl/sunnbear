"""This category holds the modified versions of the formulas of Bus, Dekker (1975)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_iii, f06_iv


class ModifiedBusDekker1975(FormulaCategory):
    """`ModifiedBusDekker1975` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.1, `BusDekker1975`, and come from its publication.
    """

    number = (1, 99, 2, 1)
    name = "Bus, Dekker (1975)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces "
        "Algorithms M and R, 2 methods with guaranteed convergence."
    )
