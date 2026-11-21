"""This category holds the formulas of Chandrupatla (1997)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1, f02_2, f03_3, f04_4, f05_5, f06_6, f07_7, f08_8, f09_9


class Chandrupatla1997(FormulaCategory):
    """`Chandrupatla1997` is the category of the formulas of 1 publication.

    Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear function
    without using derivatives. Advances in Engineering Software 28(3), 145–149.
    https://doi.org/10.1016/S0965-9978(96)00051-8.
    """

    number = (1, 1, 7)
    name = "Chandrupatla (1997)"
    description = (
        "The test problems come from the article that introduces Chandrupatla's method, a hybrid of"
        " quadratic interpolation and bisection."
    )
