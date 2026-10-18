"""This module holds 2 third parties' published tables, as test problems with the table's iteration count for
`Illinois`:

- `FORD_TABLE_4`: Table 4 of Ford (1997);
- `OLIVEIRA_TAKAHASHI_TABLE_1`: the column "Illinois" of Table 1 of Oliveira and Takahashi (2020).
"""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.ford import FordTable4Problem
from tests.solvers.paper_problems.oliveira_takahashi import OliveiraTakahashiTable1Problem

FORD_TABLE_4 = [
    FordTable4Problem.F1_I1.with_n_iterations(10),
    FordTable4Problem.F1_I2.with_n_iterations(12),
    FordTable4Problem.F1_I3.with_n_iterations(21),
    FordTable4Problem.F2_I1.with_n_iterations(8),
    FordTable4Problem.F2_I2.with_n_iterations(
        15,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve stops on an iterate whose |f(x)| is 0.994 times Ford's limit on |f(x)|",
    ),
    FordTable4Problem.F2_I3.with_n_iterations(70),
    FordTable4Problem.F3_I1.with_n_iterations(7),
    FordTable4Problem.F3_I2.with_n_iterations(29),
    FordTable4Problem.F3_I3.with_n_iterations(44),
    FordTable4Problem.F4_I1.with_n_iterations(9),
    FordTable4Problem.F4_I2.with_n_iterations(15),
    FordTable4Problem.F4_I3.with_n_iterations(33),
    FordTable4Problem.F5_I1.with_n_iterations(14),
    FordTable4Problem.F5_I2.with_n_iterations(
        27,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the interval drops below Ford's width limit one iteration early",
    ),
    FordTable4Problem.F5_I3.with_n_iterations(
        49,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve reaches f(x) == 0 one iteration early",
    ),
]

OLIVEIRA_TAKAHASHI_TABLE_1 = [
    OliveiraTakahashiTable1Problem.LAMBERT.with_n_iterations(9),
    OliveiraTakahashiTable1Problem.TRIGONOMETRIC_1.with_n_iterations(6),
    OliveiraTakahashiTable1Problem.TRIGONOMETRIC_2.with_n_iterations(
        7,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration more: iterate 7 has f(x) = 5.6e-17, the spacing between floats "
        "just below 0.5, which is the constant term of f; iterate 8 has f(x) == 0",
    ),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_1.with_n_iterations(12),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_2.with_n_iterations(11),
    OliveiraTakahashiTable1Problem.EXPONENTIAL.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.LOGARITHMIC.with_n_iterations(10),
    OliveiraTakahashiTable1Problem.POSYNOMIAL.with_n_iterations(
        15,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration more, and the table's count with the secant's zero computed as "
        "(a*fb - b*fa) / (fb - fa)",
    ),
    OliveiraTakahashiTable1Problem.WEIERSTRASS.with_n_iterations(11),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_FRACTION.with_n_iterations(13),
    OliveiraTakahashiTable1Problem.NORMAL_CDF.with_n_iterations(
        8,
        deviation=1,
        reason="the count depends on how the platform's erf rounds: `Illinois` takes the table's 8 iterations on macOS "
        "and 9 on Linux on ARM",
    ),
    OliveiraTakahashiTable1Problem.NORMAL_PDF.with_n_iterations(
        10,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration less: iterate 9 has f(x) == 0",
    ),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_3.with_n_iterations(144),
    OliveiraTakahashiTable1Problem.EXPONENTIAL_POLYNOMIAL.with_n_iterations(
        146,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration more, and the table's count with the secant's zero computed as "
        "(a*fb - b*fa) / (fb - fa)",
    ),
    OliveiraTakahashiTable1Problem.TANGENT_POLYNOMIAL.with_n_iterations(
        110,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration less, and the table's count with the secant's zero computed as "
        "(a*fb - b*fa) / (fb - fa)",
    ),
    OliveiraTakahashiTable1Problem.CIRCLES.with_n_iterations(26),
    OliveiraTakahashiTable1Problem.STEP_FUNCTION.with_n_iterations(155),
    OliveiraTakahashiTable1Problem.GEOMETRIC.with_n_iterations(
        69,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration less, and the table's count with the secant's zero computed as "
        "(a*fb - b*fa) / (fb - fa)",
    ),
    OliveiraTakahashiTable1Problem.TRUNCATED_POLYNOMIAL.with_n_iterations(38),
    OliveiraTakahashiTable1Problem.STAIRCASE.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.NOISY_LINE.with_n_iterations(
        20,
        deviation=4,
        reason=(
            "the paper does not state in which form its runs compute the secant's zero, and f has roots about 3e-6 "
            "apart between -0.1 and 0.1, so the rounding of the first iterates decides which root the solve reaches"
        ),
        observation=(
            "the solve takes 4 iterations less and reaches the root near -0.0534; with the secant's zero computed as "
            "(a*fb - b*fa) / (fb - fa), iterate 1 differs by 505 ulps, and the solve reaches the root near -0.0356 "
            "after the table's count"
        ),
    ),
    OliveiraTakahashiTable1Problem.WARSAW.with_n_iterations(12),
    OliveiraTakahashiTable1Problem.SAWTOOTH.with_n_iterations(2),
    OliveiraTakahashiTable1Problem.SAWTOOTH_CUBE.with_n_iterations(96),
]
