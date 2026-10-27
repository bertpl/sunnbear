"""This category holds the modified versions of the formulas of Alefeld, Potra, Shi (1995)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_12


class ModifiedAlefeldPotraShi1995(FormulaCategory):
    """`ModifiedAlefeldPotraShi1995` holds the modified versions of the formulas of 1 publication.

    Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous functions. ACM
    Transactions on Mathematical Software 21(3), 327–344. https://doi.org/10.1145/210089.210111. The authors' code
    is CALGO 748: https://www.netlib.org/toms/748.
    """

    number = (1, 99, 1, 6)
    name = "Alefeld, Potra, Shi (1995)"
