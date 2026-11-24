"""This category holds the formulas of Alefeld, Potra, Shi (1995)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_problem_4, f02_problem_6, f03_problem_12


class AlefeldPotraShi1995(FormulaCategory):
    """`AlefeldPotraShi1995` is the category of the formulas of 1 publication."""

    number = (1, 1, 6)
    name = "Alefeld, Potra, Shi (1995)"
    description = (
        "The test problems come from the article that introduces Algorithm 748, which encloses "
        "zeros of continuous functions."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
