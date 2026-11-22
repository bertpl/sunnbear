"""This category holds the formulas of Oliveira, Takahashi (2021)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_well_behaved_function_2,
    f02_well_behaved_function_3,
    f03_well_behaved_function_4,
    f04_well_behaved_function_5,
    f05_well_behaved_function_6,
    f06_well_behaved_function_7,
    f07_well_behaved_function_8,
    f08_well_behaved_function_9,
    f09_well_behaved_function_10,
    f10_well_behaved_function_11,
    f11_well_behaved_function_12,
    f12_ill_behaved_function_1,
    f13_ill_behaved_function_2,
    f14_ill_behaved_function_3,
    f15_ill_behaved_function_4,
    f16_ill_behaved_function_5,
    f17_ill_behaved_function_6,
    f18_ill_behaved_function_7,
    f19_ill_behaved_function_8,
    f20_ill_behaved_function_9,
    f21_ill_behaved_function_10,
    f22_ill_behaved_function_11,
    f23_ill_behaved_function_12,
    f24_equation_23,
)


class OliveiraTakahashi2021(FormulaCategory):
    """`OliveiraTakahashi2021` is the category of the formulas of 1 publication."""

    number = (1, 1, 9)
    name = "Oliveira, Takahashi (2021)"
    description = (
        "The test problems come from the article that introduces the ITP method, which improves the"
        " average performance of bisection and keeps bisection's worst-case number of iterations."
    )
    publication = Publication(
        citation=(
            "Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method average"
            " performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), Article"
            " 5. https://doi.org/10.1145/3423597. The article itself is dated December 2020."
        ),
        citation_key="Oliveira21",
        authors=("Oliveira, I. F. D.", "Takahashi, R. H. C."),
        year=2021,
        title="An enhancement of the bisection method average performance preserving minmax optimality",
        published_in="ACM Transactions on Mathematical Software",
        doi="10.1145/3423597",
    )
