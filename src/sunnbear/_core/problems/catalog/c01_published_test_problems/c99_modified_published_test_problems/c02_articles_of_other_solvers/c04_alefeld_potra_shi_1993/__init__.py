"""This category holds the modified versions of the formulas of Alefeld, Potra, Shi (1993)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_t5_1_2


class ModifiedAlefeldPotraShi1993(FormulaCategory):
    """`ModifiedAlefeldPotraShi1993` holds the modified versions of the formulas of 1 publication.

    Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear equations. Mathematics of
    Computation 61(204), 733–744. https://doi.org/10.1090/s0025-5718-1993-1192965-2.
    """

    number = (1, 99, 2, 4)
    name = "Alefeld, Potra, Shi (1993)"
