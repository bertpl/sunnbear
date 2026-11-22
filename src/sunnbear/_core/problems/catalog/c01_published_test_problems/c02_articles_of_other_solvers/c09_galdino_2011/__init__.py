"""This category holds the formulas of Galdino (2011)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_f1,
    f02_function_f2,
    f03_function_f3,
    f04_function_f4,
    f05_function_f5,
    f06_function_f6,
    f07_function_f7,
)


class Galdino2011(FormulaCategory):
    """`Galdino2011` is the category of the formulas of 1 publication."""

    number = (1, 2, 9)
    name = "Galdino (2011)"
    description = "The test problems come from the article that introduces a family of regula falsi methods."
    publication = Publication(
        citation=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011 World"
            " Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN 978-1-61284-365-0."
            " No DOI; the author's copy: http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        citation_key="Galdino11",
        authors=("Galdino, S.",),
        year=2011,
        title="A family of regula falsi root-finding methods",
        published_in="Proceedings of the 2011 World Congress on Engineering and Technology",
        url="http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543",
    )
