"""This category holds the modified versions of the formulas of textbooks."""

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


class ModifiedTextbooks(FormulaCategory):
    """`ModifiedTextbooks` is subcategory 1.99.4.

    It holds the modified versions of the formulas of subcategory 1.4.
    """

    number = (1, 99, 4)
    name = "Textbooks"
