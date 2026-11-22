"""This category holds the formulas of Parida, Gupta (2006)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_1, f02_2, f03_4


class ParidaGupta2006(FormulaCategory):
    """`ParidaGupta2006` is the category of the formulas of 1 publication."""

    number = (1, 2, 5)
    name = "Parida, Gupta (2006)"
    description = "The test problems come from the article that introduces an improved regula falsi method."
    publication = Publication(
        citation=(
            "Parida, P. K., Gupta, D. K. (2006). An improved regula-falsi method for enclosing simple zeros of"
            " nonlinear equations. Applied Mathematics and Computation 177(2), 769–776."
            " https://doi.org/10.1016/j.amc.2005.11.034. The article prints the volume and the year 2006 but no"
            " issue number; the issue number is Crossref's. The survey lists the article under 2005, the year of"
            ' its copyright line ("© 2005 Elsevier Inc.") and of its DOI; the article prints no online date.'
        ),
        citation_key="Parida06",
        authors=("Parida, P. K.", "Gupta, D. K."),
        year=2006,
        title="An improved regula-falsi method for enclosing simple zeros of nonlinear equations",
        published_in="Applied Mathematics and Computation",
        doi="10.1016/j.amc.2005.11.034",
    )
