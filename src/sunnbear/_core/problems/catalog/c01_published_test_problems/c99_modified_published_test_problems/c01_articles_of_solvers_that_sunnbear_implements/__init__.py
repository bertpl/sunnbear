"""This category holds the modified formulas of articles of solvers that sunnbear implements, grouped by source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c02_dowell_jarratt_1972,
    c04_brent_1973,
    c05_ridders_1979,
    c06_alefeld_potra_shi_1995,
    c07_chandrupatla_1997,
    c08_ford_1997,
    c09_oliveira_takahashi_2021,
    c12_gorgey_et_al_2025,
    c13_ganchovski_smith_rackauckas_tomov_traykov_2026,
    c14_gao_2026,
)


class ModifiedArticlesOfSolversThatSunnbearImplements(FormulaCategory):
    """`ModifiedArticlesOfSolversThatSunnbearImplements` holds the modified formulas of subcategory 1.1."""

    number = (1, 99, 1)
    name = "Articles of solvers that sunnbear implements"
