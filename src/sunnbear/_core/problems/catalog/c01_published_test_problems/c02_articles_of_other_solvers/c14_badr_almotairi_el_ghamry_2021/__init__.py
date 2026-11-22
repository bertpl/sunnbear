"""This category holds the formulas of Badr, Almotairi, El Ghamry (2021)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_p7, f02_p10, f03_p12, f04_p13, f05_p14


class BadrAlmotairiElGhamry2021(FormulaCategory):
    """`BadrAlmotairiElGhamry2021` is the category of the formulas of 1 publication."""

    number = (1, 2, 14)
    name = "Badr, Almotairi, El Ghamry (2021)"
    description = (
        "The test problems come from the article that introduces hybrid methods, among them one "
        "that combines trisection and false position."
    )
    publication = Publication(
        citation=(
            "Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root finding"
            " algorithms and traditional methods. Mathematics 9(11), 1306. https://doi.org/10.3390/math9111306."
        ),
        citation_key="Badr21",
        authors=("Badr, E.", "Almotairi, S.", "El Ghamry, A."),
        year=2021,
        title="A comparative study among new hybrid root finding algorithms and traditional methods",
        published_in="Mathematics",
        doi="10.3390/math9111306",
    )
