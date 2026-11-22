"""This category holds the modified versions of the formulas of Süli, Mayers (2003)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_equation_1_2, f05_equation_1_33


class ModifiedSuliMayers2003(FormulaCategory):
    """`ModifiedSuliMayers2003` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.2, `SuliMayers2003`, and come from the publication of `SuliMayers2003`.
    """

    number = (1, 99, 4, 2)
    name = "Süli, Mayers (2003)"
    description = (
        "The test problems are modified versions of those that come from chapter 1, on solving equations by "
        "iteration, of the textbook An Introduction to Numerical Analysis."
    )
