"""This category holds the formulas of Ganchovski, Traykov (2023)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_3


class GanchovskiTraykov2023(FormulaCategory):
    """`GanchovskiTraykov2023` is the category of the formulas of 1 publication."""

    number = (1, 1, 10)
    name = "Ganchovski, Traykov (2023)"
    description = (
        "The test problems come from the article that introduces the modified Anderson–Björck "
        "method, for nonlinear equations in structural mechanics."
    )
    publication = Publication(
        citation=(
            "Ganchovski, N., Traykov, A. (2023). Modified Anderson-Bjork's method for solving non-linear"
            " equations in structural mechanics. IOP Conf. Series: Materials Science and Engineering 1276,"
            " 012010. https://doi.org/10.1088/1757-899X/1276/1/012010."
        ),
        citation_key="Ganchovski23",
        authors=("Ganchovski, N.", "Traykov, A."),
        year=2023,
        title="Modified Anderson-Bjork's method for solving non-linear equations in structural mechanics",
        published_in="IOP Conf. Series: Materials Science and Engineering",
        doi="10.1088/1757-899X/1276/1/012010",
    )
