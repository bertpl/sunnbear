"""This category holds the formulas of Burkardt (2016)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_problem_p01,
    f02_problem_p02,
    f03_problem_p03,
    f04_problem_p04,
    f05_problem_p05,
    f06_problem_p06,
    f07_problem_p07,
    f08_problem_p08,
    f09_problem_p09,
    f10_problem_p10,
    f11_problem_p11,
    f12_problem_p12,
    f13_problem_p13,
    f14_problem_p14,
    f15_problem_p15,
    f16_problem_p16,
    f17_problem_p18,
    f18_problem_p19,
)


class Burkardt2016(FormulaCategory):
    """`Burkardt2016` is the category of the formulas of 1 publication."""

    number = (1, 3, 1)
    name = "Burkardt (2016)"
    description = (
        "The test problems come from TEST_ZERO, John Burkardt's collection of functions for testing"
        " root finders, in its Python version."
    )
    publication = Publication(
        citation=(
            "John Burkardt, TEST_ZERO, Python version, file `test_zero.py`,"
            " https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py, MIT license.\n\nThe file is"
            " unversioned and has no file header; the rows come from the version with sha256"
            " `658ed0a0b520eba30e87d4a08d73b444fe4f3edf14a8a94339703eca2ef9680c`. The comment of each function"
            " gives the date on which that function was last modified, and the latest is 16 October 2020, for"
            " `p16_root`. The year is 2016 because every function that the rows transcribe (`pNN_fx`, `pNN_rang`,"
            " `pNN_start` and `pNN_title`) is dated 2 December 2016 or earlier.\n\nThe file cites sources for 3 of"
            " its functions, and names a 4th origin without a reference:\n- [1] George Donovan, Arnold Miller,"
            ' Timothy Moreland, "Pathological Functions for Newton\'s Method", American Mathematical Monthly,'
            " January 1993, pages 53-58 (no DOI in the file), for `p15`.\n- [2] Peter Colwell, Solving Kepler's"
            " Equation Over Three Centuries, Willmann-Bell, 1993, and [3] Jean Meeus, Astronomical Algorithms,"
            " Willman-Bell, 1991, for `p16`.\n- [4] Cleve Moler, Numerical Computing with MATLAB, SIAM, 2004, ISBN"
            " 978-0-898716-60-3, for `p18`.\n- `p17`'s comment says that Wallis used the function to illustrate"
            " Newton's method, with no reference.\n\nThe file's `brent` solver cites Brent's 1973 book for the"
            " algorithm, not for any function."
        ),
        citation_key="TestZero16",
        authors=("John Burkardt",),
        year=2016,
        title="TEST_ZERO",
        url="https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py",
    )
