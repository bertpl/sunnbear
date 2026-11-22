"""This category holds the modified versions of the formulas of Galdino (2011)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_f4, f06_f6


class ModifiedGaldino2011(FormulaCategory):
    """`ModifiedGaldino2011` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.9, `Galdino2011`, and come from its publication.
    """

    number = (1, 99, 2, 9)
    name = "Galdino (2011)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces a family "
        "of regula falsi methods."
    )
