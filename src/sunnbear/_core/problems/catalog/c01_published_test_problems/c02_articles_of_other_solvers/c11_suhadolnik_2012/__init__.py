"""This category holds the formulas of Suhadolnik (2012)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_2,
    f02_function_4,
    f03_function_5,
    f04_function_7,
    f05_function_8,
    f06_function_9,
    f07_function_10,
    f08_function_11,
    f09_function_12,
    f10_function_13,
    f11_function_14,
    f12_function_15,
    f13_function_17,
    f14_function_18,
)


class Suhadolnik2012(FormulaCategory):
    """`Suhadolnik2012` is the category of the formulas of 1 publication."""

    number = (1, 2, 11)
    name = "Suhadolnik (2012)"
    description = "The test problems come from the article that introduces combined bracketing methods."
    publication = Publication(
        citation=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. Applied"
            " Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        citation_key="Suhadolnik12",
        authors=("Suhadolnik, A.",),
        year=2012,
        title="Combined bracketing methods for solving nonlinear equations",
        published_in="Applied Mathematics Letters",
        doi="10.1016/j.aml.2012.02.006",
    )
