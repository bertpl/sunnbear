"""This category holds the formulas of Norton (1985)."""

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
    publication = Publication(
        citation=(
            "Norton, V. (1985). Algorithm 631: Finding a bracketed zero by Larkin's method of rational"
            " interpolation. ACM Transactions on Mathematical Software 11(2), 120–134."
            " https://doi.org/10.1145/214392.214396. The author's Fortran code is Algorithm 631 of the Collected"
            " Algorithms of the ACM (CALGO), https://www.netlib.org/toms/631."
        ),
        citation_key="Norton85",
        authors=("Norton, V.",),
        year=1985,
        title="Algorithm 631: Finding a bracketed zero by Larkin's method of rational interpolation",
        published_in="ACM Transactions on Mathematical Software",
        doi="10.1145/214392.214396",
    )
