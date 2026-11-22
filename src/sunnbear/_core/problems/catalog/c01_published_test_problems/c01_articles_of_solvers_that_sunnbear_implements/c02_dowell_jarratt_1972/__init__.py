"""This category holds the formulas of Dowell, Jarratt (1972)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_table_1, f02_problem_1, f03_problem_2, f04_problem_3


class DowellJarratt1972(FormulaCategory):
    """`DowellJarratt1972` is the category of the formulas of 1 publication."""

    number = (1, 1, 2)
    name = "Dowell, Jarratt (1972)"
    description = (
        "The test problems come from the article that introduces the Pegasus method, a modified regula falsi method."
    )
    publication = Publication(
        citation=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an equation. BIT'
            " 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        citation_key="Dowell72",
        authors=("Dowell, M.", "Jarratt, P."),
        year=1972,
        title='The "Pegasus" method for computing the root of an equation',
        published_in="BIT",
        doi="10.1007/BF01932959",
    )
