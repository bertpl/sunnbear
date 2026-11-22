"""This category holds the modified versions of the formulas of Ford (1997)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_function_1


class ModifiedFord1997(FormulaCategory):
    """`ModifiedFord1997` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.8, `Ford1997`, and come from the publication of `Ford1997`.
    """

    number = (1, 99, 1, 8)
    name = "Ford (1997)"
    description = (
        "The test problems are modified versions of those that come from the article that introduces improved "
        "Illinois-type methods."
    )
