"""This category holds the modified versions of the formulas of Burkardt (2016)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_p04, f06_p06, f12_p12, f17_p18


class ModifiedBurkardt2016(FormulaCategory):
    """`ModifiedBurkardt2016` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.1, `Burkardt2016`, and come from its publication.
    """

    number = (1, 99, 3, 1)
    name = "Burkardt (2016)"
    description = (
        "The test problems are modified versions of those that come from TEST_ZERO, John Burkardt's "
        "collection of functions for testing root finders, in its Python version."
    )
