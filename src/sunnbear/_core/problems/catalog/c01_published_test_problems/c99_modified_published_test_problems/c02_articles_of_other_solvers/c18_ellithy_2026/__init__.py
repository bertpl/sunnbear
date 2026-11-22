"""This category holds the modified versions of the formulas of Ellithy (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_20, f06_21, f14_30, f20_38


class ModifiedEllithy2026(FormulaCategory):
    """`ModifiedEllithy2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.18, `Ellithy2026`, and come from its publication.
    """

    number = (1, 99, 2, 18)
    name = "Ellithy (2026)"
    description = (
        "The test problems are modified versions of those that come from the data set of the article that "
        "introduces 4 multi-phase hybrid bracketing methods."
    )
