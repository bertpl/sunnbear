"""This category holds the modified versions of the formulas of Gorgey et al. (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_equation_1, f02_equation_2, f04_equation_4


class ModifiedGorgeyEtAl2025(FormulaCategory):
    """`ModifiedGorgeyEtAl2025` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.12, `GorgeyEtAl2025`, and come from its publication.
    """

    number = (1, 99, 1, 12)
    name = "Gorgey et al. (2025)"
    description = (
        "The test problems are modified versions of those that come from an article on the efficiency of a "
        "Scilab implementation of Ridders' method."
    )
