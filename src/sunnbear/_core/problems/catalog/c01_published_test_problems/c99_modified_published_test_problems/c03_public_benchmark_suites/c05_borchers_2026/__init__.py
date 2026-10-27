"""This category holds the modified versions of the formulas of Borchers (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f12_f12, f13_5_2_2


class ModifiedBorchers2026(FormulaCategory):
    """`ModifiedBorchers2026` holds the modified versions of the formulas of 1 publication.

    Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". https://hwborchers.lima-
    city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The page is unversioned and gives no author or
    date; it is on the website of Hans W. Borchers, the author of the R package pracma. The chapter cites no source
    for its test problems.
    """

    number = (1, 99, 3, 5)
    name = "Borchers (2026)"
