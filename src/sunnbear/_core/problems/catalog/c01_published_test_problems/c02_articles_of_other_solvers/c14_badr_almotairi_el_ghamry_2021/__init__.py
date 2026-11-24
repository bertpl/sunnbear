"""This category holds the formulas of Badr, Almotairi, El Ghamry (2021)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_p7, f02_problem_p10, f03_problem_p12, f04_problem_p13, f05_problem_p14


class BadrAlmotairiElGhamry2021(FormulaCategory):
    """`BadrAlmotairiElGhamry2021` is the category of the formulas of 1 publication."""

    number = (1, 2, 14)
    name = "Badr, Almotairi, El Ghamry (2021)"
    description = (
        "The test problems come from the article that introduces hybrid methods, among them one "
        "that combines trisection and false position."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
