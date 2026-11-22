"""This category holds the formulas of Moler (2004)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_1_1,
    f02_section_1_7,
    f03_section_4_5,
    f04_section_4_4,
    f05_section_4_8,
    f06_section_4_10,
    f07_section_4_7,
    f08_section_4_7_function_3,
    f09_exercise_4_1,
    f10_function_2,
    f11_exercise_4_1_function_3,
    f12_function_4,
    f13_function_5,
    f14_exercise_4_3,
    f15_exercise_4_10_c,
)


class Moler2004(FormulaCategory):
    """`Moler2004` is the category of the formulas of 1 publication."""

    number = (1, 4, 3)
    name = "Moler (2004)"
    description = (
        "The test problems come from the textbook Numerical Computing with MATLAB: from chapter 4, "
        "on zeros and roots, and from 2 examples of chapter 1."
    )
    publication = Publication(
        citation=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); The"
            " MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web edition, 1 PDF per"
            " chapter: https://www.mathworks.com/moler/chapters.html; chapter 4:"
            " https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        citation_key="Moler04",
        authors=("Moler, C. B.",),
        year=2004,
        title="Numerical Computing with MATLAB",
        published_in="SIAM",
        url="https://www.mathworks.com/moler/chapters.html",
    )
