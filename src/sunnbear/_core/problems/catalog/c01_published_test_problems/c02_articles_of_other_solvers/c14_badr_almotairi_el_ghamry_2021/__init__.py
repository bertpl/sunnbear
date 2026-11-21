"""This category holds the formulas of Badr, Almotairi, El Ghamry (2021)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_p7, f02_p10, f03_p12, f04_p13, f05_p14


class BadrAlmotairiElGhamry2021(FormulaCategory):
    """`BadrAlmotairiElGhamry2021` is the category of the formulas of 1 publication.

    Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root finding algorithms and
    traditional methods. Mathematics 9(11), 1306. https://doi.org/10.3390/math9111306.
    """

    number = (1, 2, 14)
    name = "Badr, Almotairi, El Ghamry (2021)"
    description = (
        "The test problems come from the article that introduces hybrid methods, among them a blend"
        " of trisection and false position."
    )
