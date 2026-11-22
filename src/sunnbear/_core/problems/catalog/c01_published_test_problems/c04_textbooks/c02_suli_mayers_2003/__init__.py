"""This category holds the formulas of Süli, Mayers (2003)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_1_2, f02_example_1_1, f03_example_1_4, f04_example_1_7, f05_equation_1_33, f06_exercise_1_2


class SuliMayers2003(FormulaCategory):
    """`SuliMayers2003` is the category of the formulas of 1 publication."""

    number = (1, 4, 2)
    name = "Süli, Mayers (2003)"
    description = (
        "The test problems come from chapter 1, on solving equations by iteration, of the textbook "
        "An Introduction to Numerical Analysis."
    )
    publication = Publication(
        citation=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge University Press,"
            " Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        citation_key="Suli03",
        authors=("Süli, E.", "Mayers, D. F."),
        year=2003,
        title="An Introduction to Numerical Analysis",
        published_in="Cambridge University Press",
        doi="10.1017/CBO9780511801181",
    )
