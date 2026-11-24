"""This category holds the formulas of Gao (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_3_function_1,
    f02_section_3_function_2,
    f03_table_2_function_1,
    f04_table_2_function_2,
    f05_function_7,
)


class Gao2026(FormulaCategory):
    """`Gao2026` is the category of the formulas of 1 publication."""

    number = (1, 1, 14)
    name = "Gao (2026)"
    description = (
        "The test problems come from the article that introduces CARF, a root-finding method that "
        "interpolates with clipped powers."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
