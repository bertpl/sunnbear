"""This category holds the modified versions of the formulas of Sabharwal (2019)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f08_t2_6, f09_t2_8


class ModifiedSabharwal2019(FormulaCategory):
    """`ModifiedSabharwal2019` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.2.13, `Sabharwal2019`, and come from its publication.
    """

    number = (1, 99, 2, 13)
    name = "Sabharwal (2019)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces a hybrid "
        "of bisection and regula falsi."
    )
