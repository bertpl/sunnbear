"""This category holds the modified versions of the formulas of Atkinson (1989)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_equation_1_3_6, f06_case_3, f07_case_4, f08_problem_38_a


class ModifiedAtkinson1989(FormulaCategory):
    """`ModifiedAtkinson1989` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.4.1, `Atkinson1989`, and come from the publication of `Atkinson1989`.
    """

    number = (1, 99, 4, 1)
    name = "Atkinson (1989)"
    description = (
        "The test problems are modified versions of those that come from chapter 2, on rootfinding, of the "
        "textbook An Introduction to Numerical Analysis."
    )
