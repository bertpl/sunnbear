"""This category holds the modified formulas of Oliveira, Takahashi (2021)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f15_2_4


class ModifiedOliveiraTakahashi2021(FormulaCategory):
    """`ModifiedOliveiraTakahashi2021` is the category of the modified formulas of 1 publication.

    Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method average performance
    preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), Article 5.
    https://doi.org/10.1145/3423597. The article itself is dated December 2020.
    """

    number = (1, 99, 1, 9)
    name = "Oliveira, Takahashi (2021)"
