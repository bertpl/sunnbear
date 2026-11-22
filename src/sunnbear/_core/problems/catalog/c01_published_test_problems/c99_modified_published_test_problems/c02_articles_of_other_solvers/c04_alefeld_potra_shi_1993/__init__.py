"""This category holds the modified versions of the formulas of Alefeld, Potra, Shi (1993)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_problem_2


class ModifiedAlefeldPotraShi1993(FormulaCategory):
    """`ModifiedAlefeldPotraShi1993` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.4, `AlefeldPotraShi1993`, and come from the publication of
    `AlefeldPotraShi1993`.
    """

    number = (1, 99, 2, 4)
    name = "Alefeld, Potra, Shi (1993)"
    description = (
        "The test problems are modified versions of those that come from an article that presents methods for "
        "enclosing simple roots of nonlinear equations."
    )
