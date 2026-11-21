"""This category holds the formulas of Naghipoor, Ahmadian, Soheili (2008)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_t1_1, f02_t1_2, f03_t1_3, f04_t1_4, f05_t1_6


class NaghipoorAhmadianSoheili2008(FormulaCategory):
    """`NaghipoorAhmadianSoheili2008` is the category of the formulas of 1 publication.

    Naghipoor, J., Ahmadian, S. A., Soheili, A. R. (2008). An Improved Regula Falsi Method for Finding Simple Zeros of
    Nonlinear Equations. Applied Mathematical Sciences 2(8), 381–386. No DOI; the publisher's copy:
    https://www.m-hikari.com/ams/ams-password-2008/ams-password5-8-2008/soheiliAMS5-8-2008.pdf.
    """

    number = (1, 2, 7)
    name = "Naghipoor, Ahmadian, Soheili (2008)"
    description = "Test problems from the article that introduces an improved regula falsi method for simple zeros."
