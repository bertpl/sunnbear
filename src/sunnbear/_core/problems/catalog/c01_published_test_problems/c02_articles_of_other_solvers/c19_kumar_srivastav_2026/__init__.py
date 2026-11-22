"""This category holds the formulas of Kumar, Srivastav (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_f2, f02_function_f3, f03_function_f4, f04_function_f5, f05_function_f6, f06_appendix_a_2


class KumarSrivastav2026(FormulaCategory):
    """`KumarSrivastav2026` is the category of the formulas of 1 publication."""

    number = (1, 2, 19)
    name = "Kumar, Srivastav (2026)"
    description = "The test problems come from a preprint that introduces a randomized bracketing method."
    publication = Publication(
        citation=(
            "Kumar, D., Srivastav, S. K. (2026). A randomized bracketing method for derivative-free root finding"
            " with uniform spacing contraction. Research Square preprint."
            " https://doi.org/10.21203/rs.3.rs-10070193/v1. The article's Data Availability statement offers the"
            " authors' scripts from the corresponding author on request."
        ),
        citation_key="Kumar26",
        authors=("Kumar, D.", "Srivastav, S. K."),
        year=2026,
        title=("A randomized bracketing method for derivative-free root finding with uniform spacing contraction"),
        published_in="Research Square",
        doi="10.21203/rs.3.rs-10070193/v1",
    )
