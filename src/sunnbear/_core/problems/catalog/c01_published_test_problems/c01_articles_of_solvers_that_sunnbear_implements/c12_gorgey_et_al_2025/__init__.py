"""This category holds the formulas of Gorgey et al. (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_equation_1, f02_equation_2, f03_equation_3, f04_equation_4, f05_equation_5


class GorgeyEtAl2025(FormulaCategory):
    """`GorgeyEtAl2025` is the category of the formulas of 1 publication.

    Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method in solving nonlinear
    equations using Scilab programming. Data Analytics and Applied Mathematics 6(1), 23–35.
    https://doi.org/10.15282/daam.v6i1.11307.
    """

    number = (1, 1, 12)
    name = "Gorgey et al. (2025)"
    description = "Test problems from an article on the efficiency of Ridders' method, programmed in Scilab."
