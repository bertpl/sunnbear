"""This category holds the formulas of Burden, Faires, Burden (2016)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_section_2_pages_4748,
    f02_section_2_1_page_50,
    f03_section_2_1_example_1,
    f04_section_2_2_example_1,
    f05_example_2,
    f06_example_3,
    f07_section_2_3_example_1,
    f08_section_2_4_example_1,
    f09_exercise_2_1_1,
    f10_exercise_2_1_2,
    f11_exercise_2_1_3,
    f12_exercise_2_1_4,
    f13_exercise_2_1_5_c,
    f14_exercise_2_1_5_d,
    f15_exercise_2_1_6_a,
    f16_exercise_2_1_6_b,
    f17_exercise_2_1_6_c,
    f18_exercise_2_1_6_d,
    f19_exercise_2_1_8,
    f20_exercise_2_1_9,
    f21_exercise_2_1_10,
    f22_exercise_2_1_11,
    f23_exercise_2_1_12,
    f24_exercise_2_1_17,
    f25_exercise_2_1_18,
    f26_exercise_2_2_7,
    f27_exercise_2_2_9,
    f28_exercise_2_2_14_a,
    f29_exercise_2_3_1,
    f30_exercise_2_3_2,
    f31_exercise_2_3_5_a,
    f32_exercise_2_3_5_b,
    f33_exercise_2_3_5_d,
    f34_exercise_2_3_6_a,
    f35_exercise_2_3_6_b,
    f36_exercise_2_3_6_d,
    f37_exercise_2_3_6_e,
    f38_exercise_2_3_6_f,
    f39_exercise_2_3_13,
    f40_exercise_2_3_14,
    f41_exercise_2_4_1_a,
    f42_exercise_2_4_1_b,
    f43_exercise_2_4_1_c,
    f44_exercise_2_4_1_d,
    f45_exercise_2_4_2_a,
    f46_exercise_2_4_2_b,
    f47_exercise_2_4_2_c,
    f48_exercise_2_4_2_d,
    f49_exercise_2_4_5,
    f50_exercise_2_6_7,
)


class BurdenFairesBurden2016(FormulaCategory):
    """`BurdenFairesBurden2016` is the category of the formulas of 1 publication."""

    number = (1, 4, 7)
    name = "Burden, Faires, Burden (2016)"
    description = (
        "The test problems come from chapter 2, on equations in 1 variable, of the textbook Numerical Analysis."
    )
    publication = Publication(
        citation=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. Cengage"
            " Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and the print year"
            " 2014."
        ),
        citation_key="Burden16",
        authors=("Burden, R. L.", "Faires, J. D.", "Burden, A. M."),
        year=2016,
        title="Numerical Analysis",
        published_in="Cengage Learning",
    )
