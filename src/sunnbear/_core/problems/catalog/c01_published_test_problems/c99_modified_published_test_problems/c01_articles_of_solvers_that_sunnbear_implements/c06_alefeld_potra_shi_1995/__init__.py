"""This category holds the modified versions of the formulas of Alefeld, Potra, Shi (1995)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_12


class ModifiedAlefeldPotraShi1995(FormulaCategory):
    """`ModifiedAlefeldPotraShi1995` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.6, `AlefeldPotraShi1995`, and come from its publication.
    """

    number = (1, 99, 1, 6)
    name = "Alefeld, Potra, Shi (1995)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces "
        "Algorithm 748, which encloses zeros of continuous functions."
    )
