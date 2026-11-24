"""This category holds the formulas of Foo, Tan (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_4_2, f02_section_4_3_1


class FooTan2025(FormulaCategory):
    """`FooTan2025` is the category of the formulas of 1 publication."""

    number = (1, 2, 15)
    name = "Foo, Tan (2025)"
    description = (
        "The test problems come from a preprint that introduces a higher-order root-finding method "
        "and applies it to entropy functions."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
