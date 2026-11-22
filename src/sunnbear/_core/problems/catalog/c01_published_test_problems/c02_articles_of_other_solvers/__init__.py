"""This category holds the formulas of articles of other solvers, in 1 subcategory per source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_bus_dekker_1975,
    c02_norton_1985,
    c03_alefeld_potra_1992,
    c04_alefeld_potra_shi_1993,
    c05_parida_gupta_2006,
    c06_chen_li_2007,
    c07_naghipoor_ahmadian_soheili_2008,
    c08_gottlieb_thompson_2010,
    c09_galdino_2011,
    c10_zhang_2011,
    c11_suhadolnik_2012,
    c12_stage_2013,
    c13_sabharwal_2019,
    c14_badr_almotairi_el_ghamry_2021,
    c15_foo_tan_2025,
    c16_ismuniyarto_pinheiro_sokhna_2025,
    c17_romadani_2025,
    c18_ellithy_2026,
    c19_kumar_srivastav_2026,
    c20_li_zhou_lange_tian_2026,
)


class ArticlesOfOtherSolvers(FormulaCategory):
    """`ArticlesOfOtherSolvers` is subcategory 1.2 of the published test problems."""

    number = (1, 2)
    name = "Articles of other solvers"
    description = "The test problems come from articles on root-finding methods that sunnbear does not implement."
