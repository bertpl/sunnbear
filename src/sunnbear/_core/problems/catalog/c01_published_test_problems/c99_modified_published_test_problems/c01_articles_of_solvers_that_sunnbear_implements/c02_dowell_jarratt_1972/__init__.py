"""This category holds the modified formulas of Dowell, Jarratt (1972)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_problem_3


class ModifiedDowellJarratt1972(FormulaCategory):
    """`ModifiedDowellJarratt1972` is the category of the modified formulas of 1 publication.

    Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an equation. BIT 12(4), 503–508.
    https://doi.org/10.1007/BF01932959.
    """

    number = (1, 99, 1, 2)
    name = "Dowell, Jarratt (1972)"
