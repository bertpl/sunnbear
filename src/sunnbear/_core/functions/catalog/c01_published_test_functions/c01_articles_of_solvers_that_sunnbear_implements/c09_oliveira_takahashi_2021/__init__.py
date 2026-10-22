"""This category holds the formulas of Oliveira, Takahashi (2021).

A script generates this package from the survey of published test problems: to change it, change the survey and run
`scripts/literature_test_problems/formula_modules.py`, never this file.
"""

from sunnbear._core.functions.core import FormulaCategory

from . import (
    f01_1_2,
    f02_1_3,
    f03_1_4,
    f04_1_5,
    f05_1_6,
    f06_1_7,
    f07_1_8,
    f08_1_9,
    f09_1_10,
    f10_1_11,
    f11_1_12,
    f12_2_1,
    f13_2_2,
    f14_2_3,
    f15_2_4,
    f16_2_5,
    f17_2_6,
    f18_2_7,
    f19_2_8,
    f20_2_9,
    f21_2_10,
    f22_2_11,
    f23_2_12,
    f24_23,
)


class OliveiraTakahashi2021(FormulaCategory):
    """`OliveiraTakahashi2021` is the category of the formulas of 1 publication.

    Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method average performance
    preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), Article 5.
    https://doi.org/10.1145/3423597. The article itself is dated December 2020.
    """

    number = (1, 1, 9)
    name = "Oliveira, Takahashi (2021)"
