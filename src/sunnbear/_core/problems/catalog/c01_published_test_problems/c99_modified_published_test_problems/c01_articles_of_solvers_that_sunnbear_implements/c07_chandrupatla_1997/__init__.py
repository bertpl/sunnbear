"""This category holds the modified formulas of Chandrupatla (1997)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_2, f07_7, f08_8, f09_9


class ModifiedChandrupatla1997(FormulaCategory):
    """`ModifiedChandrupatla1997` is the category of the modified formulas of 1 publication.

    Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear function
    without using derivatives. Advances in Engineering Software 28(3), 145–149.
    https://doi.org/10.1016/S0965-9978(96)00051-8.
    """

    number = (1, 99, 1, 7)
    name = "Chandrupatla (1997)"
