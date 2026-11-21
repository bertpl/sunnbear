"""This category holds the formulas of Alefeld, Potra (1992)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1, f02_2, f03_3, f04_6, f05_10


class AlefeldPotra1992(FormulaCategory):
    """`AlefeldPotra1992` is the category of the formulas of 1 publication.

    Alefeld, G. E., Potra, F. A. (1992). Some efficient methods for enclosing simple zeros of nonlinear equations. BIT
    32(2), 334–344. https://doi.org/10.1007/bf01994885.
    """

    number = (1, 2, 3)
    name = "Alefeld, Potra (1992)"
