"""This category holds the modified versions of the formulas of Gao (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_t4_7


class ModifiedGao2026(FormulaCategory):
    """`ModifiedGao2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.14, `Gao2026`, and come from its publication.
    """

    number = (1, 99, 1, 14)
    name = "Gao (2026)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces CARF, a "
        "root-finding method that interpolates with clipped powers."
    )
