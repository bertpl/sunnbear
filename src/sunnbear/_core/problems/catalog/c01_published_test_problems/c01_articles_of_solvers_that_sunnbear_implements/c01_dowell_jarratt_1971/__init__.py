"""This category holds the formulas of Dowell, Jarratt (1971)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_table_1, f02_table_2, f03_table_3, f04_table_4, f05_table_5, f06_table_6, f07_table_7


class DowellJarratt1971(FormulaCategory):
    """`DowellJarratt1971` is the category of the formulas of 1 publication."""

    number = (1, 1, 1)
    name = "Dowell, Jarratt (1971)"
    description = (
        "The test problems come from the article that introduces the Illinois method, a modified regula falsi method."
    )
    publication = Publication(
        citation=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of an"
            " equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        )
    )
