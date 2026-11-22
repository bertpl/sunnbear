"""This category holds the formulas of Chandrupatla (1997)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_1,
    f02_function_2,
    f03_function_3,
    f04_function_4,
    f05_function_5,
    f06_function_6,
    f07_function_7,
    f08_function_8,
    f09_function_9,
)


class Chandrupatla1997(FormulaCategory):
    """`Chandrupatla1997` is the category of the formulas of 1 publication."""

    number = (1, 1, 7)
    name = "Chandrupatla (1997)"
    description = (
        "The test problems come from the article that introduces Chandrupatla's method, a hybrid of"
        " quadratic interpolation and bisection."
    )
    publication = Publication(
        citation=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a"
            " nonlinear function without using derivatives. Advances in Engineering Software 28(3), 145–149."
            " https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        citation_key="Chandrupatla97",
        authors=("Chandrupatla, T. R.",),
        year=1997,
        title=(
            "A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear function without "
            "using derivatives"
        ),
        published_in="Advances in Engineering Software",
        doi="10.1016/S0965-9978(96)00051-8",
    )
