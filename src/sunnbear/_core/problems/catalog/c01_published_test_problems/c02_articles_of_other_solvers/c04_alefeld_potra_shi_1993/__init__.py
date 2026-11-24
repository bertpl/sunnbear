"""This category holds the formulas of Alefeld, Potra, Shi (1993)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_1, f02_problem_2, f03_problem_3, f04_problem_4, f05_problem_13, f06_problem_14


class AlefeldPotraShi1993(FormulaCategory):
    """`AlefeldPotraShi1993` is the category of the formulas of 1 publication."""

    number = (1, 2, 4)
    name = "Alefeld, Potra, Shi (1993)"
    description = (
        "The test problems come from an article that presents methods for enclosing simple roots of"
        " nonlinear equations."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
