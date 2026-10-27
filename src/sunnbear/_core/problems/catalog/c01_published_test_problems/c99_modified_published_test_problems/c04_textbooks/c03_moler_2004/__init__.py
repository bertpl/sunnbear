"""This category holds the modified formulas of Moler (2004)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1_1, f02_1_7, f05_4_7_4_8, f06_4_7_4_10, f14_ex_4_3, f15_ex_4_10_c


class ModifiedMoler2004(FormulaCategory):
    """`ModifiedMoler2004` is the category of the modified formulas of 1 publication.

    Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); The MathWorks, Natick, MA
    (electronic edition). ISBN 0-89871-560-1. The author's web edition, 1 PDF per chapter:
    https://www.mathworks.com/moler/chapters.html; chapter 4:
    https://www.mathworks.com/content/dam/mathworks/mathworks- dot-com/moler/zeros.pdf.
    """

    number = (1, 99, 4, 3)
    name = "Moler (2004)"
