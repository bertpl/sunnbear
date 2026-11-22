"""This category holds the formulas of Alefeld, Potra, Shi (1993)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_1, f02_problem_2, f03_problem_3, f04_problem_4, f05_problem_13, f06_problem_14


class AlefeldPotraShi1993(FormulaCategory):
    """`AlefeldPotraShi1993` is the category of the formulas of 1 publication."""

    number = (1, 2, 4)
    name = "Alefeld, Potra, Shi (1993)"
    description = (
        "The test problems come from an article that presents methods for enclosing simple roots of"
        " nonlinear equations."
    )
    publication = Publication(
        citation=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear equations."
            " Mathematics of Computation 61(204), 733–744. https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        citation_key="Alefeld93",
        authors=("Alefeld, G.", "Potra, F. A.", "Shi, Y."),
        year=1993,
        title="On enclosing simple roots of nonlinear equations",
        published_in="Mathematics of Computation",
        doi="10.1090/s0025-5718-1993-1192965-2",
    )
