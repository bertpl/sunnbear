"""This category holds the formulas of Bus, Dekker (1975)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_2, f02_function_3, f03_function_4, f04_function_5, f05_group_iii, f06_group_iv


class BusDekker1975(FormulaCategory):
    """`BusDekker1975` is the category of the formulas of 1 publication."""

    number = (1, 2, 1)
    name = "Bus, Dekker (1975)"
    description = (
        "The test problems come from the article that introduces Algorithms M and R, 2 methods with"
        " guaranteed convergence."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
