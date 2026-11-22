"""This category holds the formulas of Naghipoor, Ahmadian, Soheili (2008)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_1, f02_equation_2, f03_equation_3, f04_equation_4, f05_equation_6


class NaghipoorAhmadianSoheili2008(FormulaCategory):
    """`NaghipoorAhmadianSoheili2008` is the category of the formulas of 1 publication."""

    number = (1, 2, 7)
    name = "Naghipoor, Ahmadian, Soheili (2008)"
    description = (
        "The test problems come from the article that introduces an improved regula falsi method for simple zeros."
    )
    publication = Publication(
        citation=(
            "Naghipoor, J., Ahmadian, S. A., Soheili, A. R. (2008). An Improved Regula Falsi Method for Finding"
            " Simple Zeros of Nonlinear Equations. Applied Mathematical Sciences 2(8), 381–386. No DOI; the"
            " publisher's copy:"
            " https://www.m-hikari.com/ams/ams-password-2008/ams-password5-8-2008/soheiliAMS5-8-2008.pdf."
        ),
        citation_key="Naghipoor08",
        authors=("Naghipoor, J.", "Ahmadian, S. A.", "Soheili, A. R."),
        year=2008,
        title="An Improved Regula Falsi Method for Finding Simple Zeros of Nonlinear Equations",
        published_in="Applied Mathematical Sciences",
        url="https://www.m-hikari.com/ams/ams-password-2008/ams-password5-8-2008/soheiliAMS5-8-2008.pdf",
    )
