"""This category holds the modified versions of the formulas of Brent (1973)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_4_1


class ModifiedBrent1973(FormulaCategory):
    """`ModifiedBrent1973` holds the modified versions of the formulas of 1 publication.

    Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, Englewood Cliffs, NJ. ISBN
    0-13-022335-2. Author's scan: https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P.
    (1975). Table Errata 520. Mathematics of Computation 29(132), 1166.
    https://doi.org/10.1090/s0025-5718-1975-0371062-9.
    """

    number = (1, 99, 1, 4)
    name = "Brent (1973)"
