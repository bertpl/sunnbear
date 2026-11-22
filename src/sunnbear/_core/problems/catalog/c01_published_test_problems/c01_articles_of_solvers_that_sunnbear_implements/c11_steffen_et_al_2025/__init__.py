"""This category holds the formulas of Steffen et al. (2025)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_6, f02_equation_8


class SteffenEtAl2025(FormulaCategory):
    """`SteffenEtAl2025` is the category of the formulas of 1 publication."""

    number = (1, 1, 11)
    name = "Steffen et al. (2025)"
    description = (
        "The test problems come from an article that guarantees a halving of the interval in "
        "Dekker's and Brent's methods."
    )
    publication = Publication(
        citation=(
            "Steffen, V., Della Pasqua, C. C., de Oliveira, M. S., da Silva, E. A. (2025). Halving interval"
            " guaranteed for Dekker and Brent root finding methods. Examples and Counterexamples 7, 100173."
            " https://doi.org/10.1016/j.exco.2024.100173."
        ),
        citation_key="Steffen25",
        authors=("Steffen, V.", "Della Pasqua, C. C.", "de Oliveira, M. S.", "da Silva, E. A."),
        year=2025,
        title="Halving interval guaranteed for Dekker and Brent root finding methods",
        published_in="Examples and Counterexamples",
        doi="10.1016/j.exco.2024.100173",
    )
