"""This category holds the formulas of Gao (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_s3_1, f02_s3_2, f03_t2_1, f04_t2_2, f05_t4_7


class Gao2026(FormulaCategory):
    """`Gao2026` is the category of the formulas of 1 publication.

    Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters 178,
    109928. https://doi.org/10.1016/j.aml.2026.109928.
    """

    number = (1, 1, 14)
    name = "Gao (2026)"
    description = (
        "Test problems from the article that introduces CARF, a root-finding method that "
        "interpolates with clipped powers."
    )
