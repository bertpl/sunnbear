"""This category holds the formulas of Borchers (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_f1,
    f02_f2,
    f03_f3,
    f04_f4,
    f05_f5,
    f06_f6,
    f07_f7,
    f08_f8,
    f09_f9,
    f10_f10,
    f11_f11,
    f12_f12,
    f13_5_2_2,
)


class Borchers2026(FormulaCategory):
    """`Borchers2026` is the category of the formulas of 1 publication.

    Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". https://hwborchers.lima-
    city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The page is unversioned and gives no author or date;
    it is on the website of Hans W. Borchers, the author of the R package pracma. The chapter cites no source for its
    test problems.
    """

    number = (1, 3, 5)
    name = "Borchers (2026)"
