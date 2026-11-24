"""This category holds the formulas of Stage (2013)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_3_4,
    f02_section_3_5,
    f03_section_3_6,
    f04_section_3_7,
    f05_section_3_8,
    f06_section_3_9,
    f07_section_3_10,
    f08_section_3_11,
    f09_section_3_13,
)


class Stage2013(FormulaCategory):
    """`Stage2013` is the category of the formulas of 1 publication."""

    number = (1, 2, 12)
    name = "Stage (2013)"
    description = (
        "The test problems come from an article that comments on an improvement to Brent's method "
        "and compares 7 methods."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
