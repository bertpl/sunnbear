"""This category holds the formulas of Stage (2013)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_3_4,
    f02_section_3_5,
    f03_section_3_6,
    f04_section_3_7,
    f05_section_3_8,
    f06_section_3_9,
    f07_section_3_10,
    f08_section_3_11,
    f09_section_3_13,
)


class Stage2013(FormulaCategory):
    """`Stage2013` is the category of the formulas of 1 publication."""

    number = (1, 2, 12)
    name = "Stage (2013)"
    description = (
        "The test problems come from an article that comments on an improvement to Brent's method "
        "and compares 7 methods."
    )
    publication = Publication(
        citation=(
            "Stage, S. A. (2013). Comments on An Improvement to the Brent's Method. International Journal of"
            " Experimental Algorithms 4(1), 1–16. No DOI; the publisher's PDF:"
            " https://www.cscjournals.org/manuscript/Journals/IJEA/Volume4/Issue1/IJEA-33.pdf."
        ),
        citation_key="Stage13",
        authors=("Stage, S. A.",),
        year=2013,
        title="Comments on An Improvement to the Brent's Method",
        published_in="International Journal of Experimental Algorithms",
        url="https://www.cscjournals.org/manuscript/Journals/IJEA/Volume4/Issue1/IJEA-33.pdf",
    )
