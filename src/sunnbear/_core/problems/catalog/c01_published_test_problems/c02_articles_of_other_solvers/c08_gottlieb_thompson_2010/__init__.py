"""This category holds the formulas of Gottlieb, Thompson (2010)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1, f02_3, f03_7


class GottliebThompson2010(FormulaCategory):
    """`GottliebThompson2010` is the category of the formulas of 1 publication.

    Gottlieb, R. G., Thompson, B. F. (2010). Bisected direct quadratic regula falsi. Applied Mathematical Sciences
    4(15), 709–718. No DOI; the publisher's copy:
    http://www.m-hikari.com/ams/ams-2010/ams-13-16-2010/gottliebAMS13-16-2010.pdf.
    """

    number = (1, 2, 8)
    name = "Gottlieb, Thompson (2010)"
    description = "Test problems from the article that introduces bisected direct quadratic regula falsi."
