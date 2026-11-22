"""This category holds the formulas of Gottlieb, Thompson (2010)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_test_1, f02_test_3, f03_test_7


class GottliebThompson2010(FormulaCategory):
    """`GottliebThompson2010` is the category of the formulas of 1 publication."""

    number = (1, 2, 8)
    name = "Gottlieb, Thompson (2010)"
    description = (
        "The test problems come from the article that introduces the bisected direct quadratic regula falsi method."
    )
    publication = Publication(
        citation=(
            "Gottlieb, R. G., Thompson, B. F. (2010). Bisected direct quadratic regula falsi. Applied"
            " Mathematical Sciences 4(15), 709–718. No DOI; the publisher's copy:"
            " http://www.m-hikari.com/ams/ams-2010/ams-13-16-2010/gottliebAMS13-16-2010.pdf."
        ),
        citation_key="Gottlieb10",
        authors=("Gottlieb, R. G.", "Thompson, B. F."),
        year=2010,
        title="Bisected direct quadratic regula falsi",
        published_in="Applied Mathematical Sciences",
        url="http://www.m-hikari.com/ams/ams-2010/ams-13-16-2010/gottliebAMS13-16-2010.pdf",
    )
