"""This category holds the formulas of Dowell, Jarratt (1971)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_table_1, f02_table_2, f03_table_3, f04_table_4, f05_table_5, f06_table_6, f07_table_7


class DowellJarratt1971(FormulaCategory):
    """`DowellJarratt1971` is the category of the formulas of 1 publication."""

    number = (1, 1, 1)
    name = "Dowell, Jarratt (1971)"
    description = (
        "The test problems come from the article that introduces the Illinois method, a modified regula falsi method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
