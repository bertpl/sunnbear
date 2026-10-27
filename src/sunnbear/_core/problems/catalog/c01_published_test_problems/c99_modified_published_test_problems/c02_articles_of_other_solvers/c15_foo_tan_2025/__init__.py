"""This category holds the modified versions of the formulas of Foo, Tan (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_4_2, f02_4_3_1


class ModifiedFooTan2025(FormulaCategory):
    """`ModifiedFooTan2025` holds the modified versions of the formulas of 1 publication.

    Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. arXiv preprint
    2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897 (https://arxiv.org/abs/2509.20897v1).
    """

    number = (1, 99, 2, 15)
    name = "Foo, Tan (2025)"
