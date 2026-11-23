"""This category holds the formulas of SciPy (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_f1,
    f02_function_f2,
    f03_function_f3,
    f04_function_f4,
    f05_function_f5,
    f06_function_f6,
    f07_function_aps14_f,
    f08_function_aps15_f,
)


class Scipy2026(FormulaCategory):
    """`Scipy2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 8)
    name = "SciPy (2026)"
    description = "The test problems come from the module of test problems for SciPy's root finders, release 1.18.1."
    publication = Publication(
        citation=(
            "SciPy 1.18.1 (2026), module `scipy/optimize/_tstutils.py`, "
            "https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py."
        ),
        citation_key="SciPy26",
        year=2026,
        title="SciPy",
        url="https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py",
    )
