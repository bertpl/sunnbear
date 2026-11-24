"""This category holds the formulas of Li, Zhou, Lange, Tian (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_example_1, f02_example_3, f03_section_7_1, f04_appendix_d, f05_section_7_3


class LiZhouLangeTian2026(FormulaCategory):
    """`LiZhouLangeTian2026` is the category of the formulas of 1 publication."""

    number = (1, 2, 20)
    name = "Li, Zhou, Lange, Tian (2026)"
    description = "The test problems come from the article that introduces the upper-crossing/solution algorithm."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
