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
            "John Burkardt, TEST_ZERO, Python version (2016), file `test_zero.py`, "
            "https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py, MIT license."
        ),
        citation_key="TestZero16",
        authors=("John Burkardt",),
        year=2016,
        title="TEST_ZERO",
        url="https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py",
    )
