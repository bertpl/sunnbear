"""This category holds the formulas of GSL (2024)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_func1, f02_func2, f03_func3, f04_func4, f05_func6, f06_sin_f, f07_cos_f


class Gsl2024(FormulaCategory):
    """`Gsl2024` is the category of the formulas of 1 publication."""

    number = (1, 3, 2)
    name = "GSL (2024)"
    description = (
        "The test problems come from the tests of the root finders of the GNU Scientific Library, release 2.8."
    )
    publication = Publication(
        citation=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` (copyright"
            " Reid Priedhorsky, Brian Gough),"
            " https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite no source"
            " for their functions."
        ),
        citation_key="GSL24",
        authors=("Reid Priedhorsky", "Brian Gough"),
        year=2024,
        title="GNU Scientific Library (GSL)",
        url="https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8",
    )
