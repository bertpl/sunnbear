"""This category holds the modified formulas of Ridders (1979)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_iii_2


class ModifiedRidders1979(FormulaCategory):
    """`ModifiedRidders1979` is the category of the modified formulas of 1 publication.

    Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous function. IEEE
    Transactions on Circuits and Systems 26(11), 979–980. https://doi.org/10.1109/TCS.1979.1084580.
    """

    number = (1, 99, 1, 5)
    name = "Ridders (1979)"
