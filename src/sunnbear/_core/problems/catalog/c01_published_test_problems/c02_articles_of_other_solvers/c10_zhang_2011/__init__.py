"""This category holds the formulas of Zhang (2011)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_3


class Zhang2011(FormulaCategory):
    """`Zhang2011` is the category of the formulas of 1 publication."""

    number = (1, 2, 10)
    name = "Zhang (2011)"
    description = "The test problems come from the article that introduces an improvement to Brent's method."
    publication = Publication(
        citation=(
            "Zhang, Z. (2011). An Improvement to the Brent's Method. International Journal of Experimental"
            " Algorithms 2(1), 21–26. No DOI; the publisher's page:"
            " https://www.cscjournals.org/library/manuscriptinfo.php?mc=IJEA-7."
        ),
        citation_key="Zhang11",
        authors=("Zhang, Z.",),
        year=2011,
        title="An Improvement to the Brent's Method",
        published_in="International Journal of Experimental Algorithms",
        url="https://www.cscjournals.org/library/manuscriptinfo.php?mc=IJEA-7",
    )
