"""This category holds the formulas of Brent (1973)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_t4_1_r1_2, f02_t4_1_r3, f03_4_1, f04_4_2


class Brent1973(FormulaCategory):
    """`Brent1973` is the category of the formulas of 1 publication."""

    number = (1, 1, 4)
    name = "Brent (1973)"
    description = (
        "The test problems come from chapter 4 of the book Algorithms for Minimization without "
        "Derivatives, which presents Brent's method."
    )
    publication = Publication(
        citation=(
            "Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, Englewood"
            " Cliffs, NJ. ISBN 0-13-022335-2. Author's scan:"
            " https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975). Table Errata"
            " 520. Mathematics of Computation 29(132), 1166. https://doi.org/10.1090/s0025-5718-1975-0371062-9."
        ),
        citation_key="Brent73",
        authors=("Brent, R. P.",),
        year=1973,
        title="Algorithms for Minimization without Derivatives",
        published_in="Prentice-Hall",
        url="https://maths-people.anu.edu.au/~brent/pub/pub011.html",
    )
