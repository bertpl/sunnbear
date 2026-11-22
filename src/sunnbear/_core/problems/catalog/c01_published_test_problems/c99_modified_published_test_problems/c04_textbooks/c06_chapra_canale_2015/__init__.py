"""This category holds the modified versions of the formulas of Chapra, Canale (2015)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_equation_pt2_3, f02_example_5_2, f18_problem_5_10, f20_problem_5_15


class ModifiedChapraCanale2015(FormulaCategory):
    """`ModifiedChapraCanale2015` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.6, `ChapraCanale2015`, and come from the publication of
    `ChapraCanale2015`.
    """

    number = (1, 99, 4, 6)
    name = "Chapra, Canale (2015)"
    description = (
        "The test problems are modified versions of those that come from Part Two, on roots of equations, of "
        "the textbook Numerical Methods for Engineers."
    )
