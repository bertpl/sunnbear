"""This category holds the modified versions of the formulas of Borchers (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f12_f12, f13_5_2_2


class ModifiedBorchers2026(FormulaCategory):
    """`ModifiedBorchers2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.5, `Borchers2026`, and come from the publication of `Borchers2026`.
    """

    number = (1, 99, 3, 5)
    name = "Borchers (2026)"
    description = (
        "The test problems are modified versions of those that come from the chapter on root finding of the "
        "pracma Handbook, which documents the R package pracma."
    )
