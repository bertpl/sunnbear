"""This category holds the formulas of Romadani (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_5_1, f02_section_5_2, f03_section_5_3, f04_section_5_4


class Romadani2025(FormulaCategory):
    """`Romadani2025` is the category of the formulas of 1 publication."""

    number = (1, 2, 17)
    name = "Romadani (2025)"
    description = "The test problems come from an article on Python implementations of classical root-finding methods."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
