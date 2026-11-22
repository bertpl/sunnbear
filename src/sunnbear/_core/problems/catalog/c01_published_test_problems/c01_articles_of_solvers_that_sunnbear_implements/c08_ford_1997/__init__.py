"""This category holds the formulas of Ford (1997)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_1, f02_function_2, f03_function_3, f04_function_4, f05_function_5


class Ford1997(FormulaCategory):
    """`Ford1997` is the category of the formulas of 1 publication."""

    number = (1, 1, 8)
    name = "Ford (1997)"
    description = "The test problems come from the article that introduces improved Illinois-type methods."
    publication = Publication(
        citation=(
            "Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia"
            " Iranica 4(1&2), 28–34. The article has no working DOI: the journal's page,"
            " https://scientiairanica.sharif.edu/article_21758.html, lists 10.24200/sci.2020.21758, which doi.org"
            " does not resolve. An earlier version is the University of Essex technical report CSM-257 (1995)."
        ),
        citation_key="Ford97",
        authors=("Ford, J. A.",),
        year=1997,
        title="Improved Illinois-type methods for the solution of nonlinear equations",
        published_in="Scientia Iranica",
        url="https://scientiairanica.sharif.edu/article_21758.html",
    )
