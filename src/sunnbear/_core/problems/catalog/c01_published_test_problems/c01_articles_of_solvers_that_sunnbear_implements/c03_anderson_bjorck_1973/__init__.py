"""This category holds the formulas of Anderson, Björck (1973)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_exercise_6


class AndersonBjorck1973(FormulaCategory):
    """`AndersonBjorck1973` is the category of the formulas of 1 publication."""

    number = (1, 1, 3)
    name = "Anderson, Björck (1973)"
    description = (
        "The test problems come from the article that introduces the Anderson–Björck method, a "
        "regula falsi method of high order."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
