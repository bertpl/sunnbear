"""This category holds the modified versions of the formulas of Oliveira, Takahashi (2021)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f15_2_4


class ModifiedOliveiraTakahashi2021(FormulaCategory):
    """`ModifiedOliveiraTakahashi2021` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.9, `OliveiraTakahashi2021`, and come from its publication.
    """

    number = (1, 99, 1, 9)
    name = "Oliveira, Takahashi (2021)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces the ITP "
        "method, which improves the average performance of bisection and keeps bisection's worst-case number "
        "of iterations."
    )
