"""This category holds the modified versions of the formulas of Dowell, Jarratt (1972)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_problem_3


class ModifiedDowellJarratt1972(FormulaCategory):
    """`ModifiedDowellJarratt1972` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.2, `DowellJarratt1972`, and come from the publication of
    `DowellJarratt1972`.
    """

    number = (1, 99, 1, 2)
    name = "Dowell, Jarratt (1972)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces the "
        "Pegasus method, a modified regula falsi method."
    )
