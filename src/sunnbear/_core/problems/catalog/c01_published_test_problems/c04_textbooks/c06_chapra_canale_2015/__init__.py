"""This category holds the formulas of Chapra, Canale (2015)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_pt2_3,
    f02_ex_5_2,
    f03_ex_5_6,
    f04_7_7_1,
    f05_fig_7_8,
    f06_8_2,
    f07_8_3,
    f08_8_4_8_21,
    f09_8_4_8_23,
    f10_prob_5_1,
    f11_prob_5_2,
    f12_prob_5_3,
    f13_prob_5_4,
    f14_prob_5_5,
    f15_prob_5_6,
    f16_prob_5_7,
    f17_prob_5_8,
    f18_prob_5_10,
    f19_prob_5_11,
    f20_prob_5_15,
    f21_prob_5_16,
    f22_prob_5_17,
    f23_prob_5_18,
    f24_prob_6_13,
    f25_prob_6_17,
    f26_prob_8_5,
    f27_prob_8_15,
    f28_prob_8_33,
    f29_prob_8_39,
)


class ChapraCanale2015(FormulaCategory):
    """`ChapraCanale2015` is the category of the formulas of 1 publication."""

    number = (1, 4, 6)
    name = "Chapra, Canale (2015)"
    description = (
        "The test problems come from Part Two, on roots of equations, of the textbook Numerical Methods for Engineers."
    )
    publication = Publication(
        citation=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. McGraw-Hill"
            " Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in 2021."
        ),
        citation_key="Chapra15",
        authors=("Chapra, S. C.", "Canale, R. P."),
        year=2015,
        title="Numerical Methods for Engineers",
        published_in="McGraw-Hill Education",
    )
