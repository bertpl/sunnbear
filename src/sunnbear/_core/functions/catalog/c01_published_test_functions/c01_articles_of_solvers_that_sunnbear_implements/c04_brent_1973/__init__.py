"""This category holds the formulas of Brent (1973).

A script generates this package from the survey of published test problems: to change it, change the survey and run
`scripts/literature_test_problems/formula_modules.py`, never this file.
"""

from sunnbear._core.functions.core import FormulaCategory

from . import f01_t4_1_r1_2, f02_t4_1_r3, f03_4_1, f04_4_2


class Brent1973(FormulaCategory):
    """`Brent1973` is the category of the formulas of 1 publication.

    Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, Englewood Cliffs, NJ. ISBN
    0-13-022335-2. Author's scan: https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975).
    Table Errata 520. Mathematics of Computation, p. 1166.
    """

    number = (1, 1, 4)
    name = "Brent (1973)"
