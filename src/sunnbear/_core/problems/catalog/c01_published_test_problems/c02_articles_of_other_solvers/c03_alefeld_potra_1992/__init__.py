"""This category holds the formulas of Alefeld, Potra (1992)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_1, f02_problem_2, f03_problem_3, f04_problem_6, f05_problem_10


class AlefeldPotra1992(FormulaCategory):
    """`AlefeldPotra1992` is the category of the formulas of 1 publication."""

    number = (1, 2, 3)
    name = "Alefeld, Potra (1992)"
    description = "The test problems come from an article that presents efficient methods for enclosing simple zeros."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
