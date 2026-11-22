"""This category holds the modified versions of the formulas of roots-fortran (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_2627, f30_8688, f33_9394, f41_150


class ModifiedRootsFortran2025(FormulaCategory):
    """`ModifiedRootsFortran2025` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.3, `RootsFortran2025`, and come from the publication of
    `RootsFortran2025`.
    """

    number = (1, 99, 3, 3)
    name = "roots-fortran (2025)"
    description = (
        "The test problems are modified versions of those that come from the test program of roots-fortran, a "
        "Fortran library of root finders."
    )
