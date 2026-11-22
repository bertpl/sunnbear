"""This category holds the modified versions of the formulas of Ganchovski (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_f100


class ModifiedGanchovski2026(FormulaCategory):
    """`ModifiedGanchovski2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.4, `Ganchovski2026`, and come from the publication of `Ganchovski2026`.
    """

    number = (1, 99, 3, 4)
    name = "Ganchovski (2026)"
    description = (
        "The test problems are modified versions of those that come from Root-finding Test Functions, the "
        "collection of functions in the repository of the modified Anderson–Björck method."
    )
