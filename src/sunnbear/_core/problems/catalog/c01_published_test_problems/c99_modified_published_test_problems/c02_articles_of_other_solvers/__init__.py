"""This category holds the modified formulas of articles of other solvers, grouped by source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_bus_dekker_1975,
    c04_alefeld_potra_shi_1993,
    c09_galdino_2011,
    c13_sabharwal_2019,
    c15_foo_tan_2025,
    c18_ellithy_2026,
)


class ModifiedArticlesOfOtherSolvers(FormulaCategory):
    """`ModifiedArticlesOfOtherSolvers` holds the modified formulas of subcategory 1.2."""

    number = (1, 99, 2)
    name = "Articles of other solvers"
