"""This category holds the formulas of Romadani (2025)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_5_1, f02_section_5_2, f03_section_5_3, f04_section_5_4


class Romadani2025(FormulaCategory):
    """`Romadani2025` is the category of the formulas of 1 publication."""

    number = (1, 2, 17)
    name = "Romadani (2025)"
    description = "The test problems come from an article on Python implementations of classical root-finding methods."
    publication = Publication(
        citation=(
            "Romadani, M. N. H. (2025). From Theory to Code: Transforming Classical Root-Finding Methods into"
            " Efficient Python Implementations. ICCK Journal of Applied Mathematics 1(3), 154–189."
            " https://doi.org/10.62762/jam.2025.840767."
        ),
        citation_key="Romadani25",
        authors=("Romadani, M. N. H.",),
        year=2025,
        title=(
            "From Theory to Code: Transforming Classical Root-Finding Methods into Efficient Python Implementations"
        ),
        published_in="ICCK Journal of Applied Mathematics",
        doi="10.62762/jam.2025.840767",
    )
