"""This category holds the formulas of Norton (1985)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_2,
    f02_function_5,
    f03_function_6,
    f04_function_8,
    f05_function_9,
    f06_function_10,
    f07_the_driver_of_the_author_s_code,
)


class Norton1985(FormulaCategory):
    """`Norton1985` is the category of the formulas of 1 publication."""

    number = (1, 2, 2)
    name = "Norton (1985)"
    description = (
        "The test problems come from the article that introduces Algorithm 631, which finds a "
        "bracketed zero by Larkin's method of rational interpolation."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
