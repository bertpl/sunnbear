"""This category holds the formulas of GSL (2024)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_func1,
    f02_function_func2,
    f03_function_func3,
    f04_function_func4,
    f05_function_func6,
    f06_function_sin_f,
    f07_function_cos_f,
)


class Gsl2024(FormulaCategory):
    """`Gsl2024` is the category of the formulas of 1 publication."""

    number = (1, 3, 2)
    name = "GSL (2024)"
    description = (
        "The test problems come from the tests of the root finders of the GNU Scientific Library, release 2.8."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
