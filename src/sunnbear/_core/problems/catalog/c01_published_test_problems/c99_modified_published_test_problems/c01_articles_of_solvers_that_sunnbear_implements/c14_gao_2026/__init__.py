"""This category holds the modified formulas of Gao (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_t4_7


class ModifiedGao2026(FormulaCategory):
    """`ModifiedGao2026` is the category of the modified formulas of 1 publication.

    Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters 178,
    109928. https://doi.org/10.1016/j.aml.2026.109928.
    """

    number = (1, 99, 1, 14)
    name = "Gao (2026)"
