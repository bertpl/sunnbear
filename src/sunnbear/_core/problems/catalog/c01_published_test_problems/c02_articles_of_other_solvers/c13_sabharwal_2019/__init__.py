"""This category holds the formulas of Sabharwal (2019)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_figure_1,
    f02_figure_2,
    f03_figure_3,
    f04_figure_4,
    f05_function_1,
    f06_function_4,
    f07_function_5,
    f08_function_6,
    f09_function_8,
    f10_function_10,
    f11_function_11,
)


class Sabharwal2019(FormulaCategory):
    """`Sabharwal2019` is the category of the formulas of 1 publication."""

    number = (1, 2, 13)
    name = "Sabharwal (2019)"
    description = "The test problems come from the article that introduces a hybrid of bisection and regula falsi."
    publication = Publication(
        citation=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula Falsi"
            " Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        citation_key="Sabharwal19",
        authors=("Sabharwal, C. L.",),
        year=2019,
        title="Blended Root Finding Algorithm Outperforms Bisection and Regula Falsi Algorithms",
        published_in="Mathematics",
        doi="10.3390/math7111118",
    )
