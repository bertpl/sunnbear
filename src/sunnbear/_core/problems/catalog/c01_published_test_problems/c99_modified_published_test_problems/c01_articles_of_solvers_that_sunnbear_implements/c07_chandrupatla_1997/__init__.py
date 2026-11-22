"""This category holds the modified versions of the formulas of Chandrupatla (1997)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_2, f07_7, f08_8, f09_9


class ModifiedChandrupatla1997(FormulaCategory):
    """`ModifiedChandrupatla1997` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.7, `Chandrupatla1997`, and come from the publication of
    `Chandrupatla1997`.
    """

    number = (1, 99, 1, 7)
    name = "Chandrupatla (1997)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces "
        "Chandrupatla's method, a hybrid of quadratic interpolation and bisection."
    )
