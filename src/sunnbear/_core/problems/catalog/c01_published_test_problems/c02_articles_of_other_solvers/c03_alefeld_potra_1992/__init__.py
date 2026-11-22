"""This category holds the formulas of Alefeld, Potra (1992)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_1, f02_problem_2, f03_problem_3, f04_problem_6, f05_problem_10


class AlefeldPotra1992(FormulaCategory):
    """`AlefeldPotra1992` is the category of the formulas of 1 publication."""

    number = (1, 2, 3)
    name = "Alefeld, Potra (1992)"
    description = "The test problems come from an article that presents efficient methods for enclosing simple zeros."
    publication = Publication(
        citation=(
            "Alefeld, G. E., Potra, F. A. (1992). Some efficient methods for enclosing simple zeros of nonlinear"
            " equations. BIT 32(2), 334–344. https://doi.org/10.1007/bf01994885."
        ),
        citation_key="Alefeld92",
        authors=("Alefeld, G. E.", "Potra, F. A."),
        year=1992,
        title="Some efficient methods for enclosing simple zeros of nonlinear equations",
        published_in="BIT",
        doi="10.1007/bf01994885",
    )
