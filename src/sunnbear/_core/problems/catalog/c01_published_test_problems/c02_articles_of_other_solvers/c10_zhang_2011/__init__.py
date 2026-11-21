"""This category holds the formulas of Zhang (2011)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_3


class Zhang2011(FormulaCategory):
    """`Zhang2011` is the category of the formulas of 1 publication.

    Zhang, Z. (2011). An Improvement to the Brent's Method. International Journal of Experimental Algorithms 2(1),
    21–26. No DOI; the publisher's page: https://www.cscjournals.org/library/manuscriptinfo.php?mc=IJEA-7.
    """

    number = (1, 2, 10)
    name = "Zhang (2011)"
