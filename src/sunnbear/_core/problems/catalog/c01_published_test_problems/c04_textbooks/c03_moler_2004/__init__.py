"""This category holds the formulas of Moler (2004)."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_1_1,
    f02_1_7,
    f03_4_1,
    f04_4_3,
    f05_4_7_4_8,
    f06_4_7_4_10,
    f07_4_7_ex_4_1,
    f08_4_7_3,
    f09_ex_4_1,
    f10_ex_4_1_2,
    f11_ex_4_1_3,
    f12_ex_4_1_4,
    f13_ex_4_1_5,
    f14_ex_4_3,
    f15_ex_4_10_c,
)


class Moler2004(FormulaCategory):
    """`Moler2004` is the category of the formulas of 1 publication.

    Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); The MathWorks, Natick, MA
    (electronic edition). ISBN 0-89871-560-1. The author's web edition, 1 PDF per chapter:
    https://www.mathworks.com/moler/chapters.html; chapter 4: https://www.mathworks.com/content/dam/mathworks/mathworks-
    dot-com/moler/zeros.pdf.
    """

    number = (1, 4, 3)
    name = "Moler (2004)"
    description = (
        "The test problems come from the textbook Numerical Computing with MATLAB: from chapter 4, "
        "on zeros and roots, and from 2 examples of chapter 1."
    )
