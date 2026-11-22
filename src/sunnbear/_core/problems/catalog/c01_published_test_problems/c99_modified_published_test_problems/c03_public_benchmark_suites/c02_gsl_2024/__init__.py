"""This category holds the modified versions of the formulas of GSL (2024)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_func3, f05_func6


class ModifiedGsl2024(FormulaCategory):
    """`ModifiedGsl2024` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.2, `Gsl2024`, and come from its publication.
    """

    number = (1, 99, 3, 2)
    name = "GSL (2024)"
    description = (
        "The test problems are modified versions of those that come from the tests of the root finders of the "
        "GNU Scientific Library, release 2.8."
    )
