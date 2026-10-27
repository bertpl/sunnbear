"""This category holds the modified versions of the formulas of Sabharwal (2019)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f08_t2_6, f09_t2_8


class ModifiedSabharwal2019(FormulaCategory):
    """`ModifiedSabharwal2019` holds the modified versions of the formulas of 1 publication.

    Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula Falsi Algorithms.
    Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118.
    """

    number = (1, 99, 2, 13)
    name = "Sabharwal (2019)"
