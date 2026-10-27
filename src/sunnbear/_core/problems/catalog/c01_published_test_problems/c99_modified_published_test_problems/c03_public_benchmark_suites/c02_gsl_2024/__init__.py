"""This category holds the modified formulas of GSL (2024)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f03_func3, f05_func6


class ModifiedGsl2024(FormulaCategory):
    """`ModifiedGsl2024` is the category of the modified formulas of 1 publication.

    GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` (copyright Reid
    Priedhorsky, Brian Gough), https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files
    cite no source for their functions.
    """

    number = (1, 99, 3, 2)
    name = "GSL (2024)"
