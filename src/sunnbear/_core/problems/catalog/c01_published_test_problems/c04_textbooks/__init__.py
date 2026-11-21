"""This category holds the formulas of textbooks, in 1 subcategory per source."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_atkinson_1989,
    c02_suli_mayers_2003,
    c03_moler_2004,
    c04_bradie_2006,
    c05_epperson_2013,
    c06_chapra_canale_2015,
    c07_burden_faires_burden_2016,
)


class Textbooks(FormulaCategory):
    """`Textbooks` is subcategory 1.4 of the published test problems."""

    number = (1, 4)
    name = "Textbooks"
    description = "The test problems come from the examples and exercises of textbooks on numerical analysis."
