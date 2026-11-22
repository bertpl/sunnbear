"""This category holds the formulas of Gao (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_3_function_1,
    f02_section_3_function_2,
    f03_table_2_function_1,
    f04_table_2_function_2,
    f05_function_7,
)


class Gao2026(FormulaCategory):
    """`Gao2026` is the category of the formulas of 1 publication."""

    number = (1, 1, 14)
    name = "Gao (2026)"
    description = (
        "The test problems come from the article that introduces CARF, a root-finding method that "
        "interpolates with clipped powers."
    )
    publication = Publication(
        citation=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics"
            " Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        citation_key="Gao26",
        authors=("Gao, F.",),
        year=2026,
        title="Fast and stable root-finding using clipped power interpolations",
        published_in="Applied Mathematics Letters",
        doi="10.1016/j.aml.2026.109928",
    )
