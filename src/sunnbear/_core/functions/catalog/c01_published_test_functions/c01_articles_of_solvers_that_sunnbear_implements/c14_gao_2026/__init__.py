"""This category holds the formulas of Gao (2026).

A script generates this package from the survey of published test problems: to change it, change the survey and run
`scripts/literature_test_problems/formula_modules.py`, never this file.
"""

from sunnbear._core.functions.core import FormulaCategory

from . import f01_s3_1, f02_s3_2, f03_t2_1, f04_t2_2, f05_t4_7, f06_t4_8, f07_t4_9


class Gao2026(FormulaCategory):
    """`Gao2026` is the category of the formulas of 1 publication.

    Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters 178,
    109928. https://doi.org/10.1016/j.aml.2026.109928.
    """

    number = (1, 1, 14)
    name = "Gao (2026)"
