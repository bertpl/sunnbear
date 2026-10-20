"""This module holds `TABLE_4_BY_VARIANT`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
the method of each variant of `Ford`."""

from sunnbear.solvers import FordVariant
from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.ford import FordTable4Problem

# On most rows of function 5 where `Ford` stops 1 iteration before Ford's count, it reaches f(x) == 0.
_REACHES_ZERO_ONE_ITERATION_EARLY = "the solve reaches f(x) == 0 one iteration early"

# `TABLE_4_BY_VARIANT` maps each variant to the table's problems, in the table's order, each with the table's iteration
# count for the variant's method.
TABLE_4_BY_VARIANT = {
    FordVariant.METHOD_1: [
        FordTable4Problem.F1_I1.with_n_iterations(5),
        FordTable4Problem.F1_I2.with_n_iterations(10),
        FordTable4Problem.F1_I3.with_n_iterations(13),
        FordTable4Problem.F2_I1.with_n_iterations(8),
        FordTable4Problem.F2_I2.with_n_iterations(20),
        FordTable4Problem.F2_I3.with_n_iterations(65),
        FordTable4Problem.F3_I1.with_n_iterations(6),
        FordTable4Problem.F3_I2.with_n_iterations(15),
        FordTable4Problem.F3_I3.with_n_iterations(15),
        FordTable4Problem.F4_I1.with_n_iterations(10),
        FordTable4Problem.F4_I2.with_n_iterations(11),
        FordTable4Problem.F4_I3.with_n_iterations(16),
        FordTable4Problem.F5_I1.with_n_iterations(
            9,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=_REACHES_ZERO_ONE_ITERATION_EARLY,
        ),
        FordTable4Problem.F5_I2.with_n_iterations(
            15,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=_REACHES_ZERO_ONE_ITERATION_EARLY,
        ),
        FordTable4Problem.F5_I3.with_n_iterations(
            19,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=_REACHES_ZERO_ONE_ITERATION_EARLY,
        ),
    ],
    FordVariant.METHOD_3: [
        FordTable4Problem.F1_I1.with_n_iterations(7),
        FordTable4Problem.F1_I2.with_n_iterations(9),
        FordTable4Problem.F1_I3.with_n_iterations(13),
        FordTable4Problem.F2_I1.with_n_iterations(7),
        FordTable4Problem.F2_I2.with_n_iterations(17),
        FordTable4Problem.F2_I3.with_n_iterations(65),
        FordTable4Problem.F3_I1.with_n_iterations(5),
        FordTable4Problem.F3_I2.with_n_iterations(12),
        FordTable4Problem.F3_I3.with_n_iterations(15),
        FordTable4Problem.F4_I1.with_n_iterations(9),
        FordTable4Problem.F4_I2.with_n_iterations(12),
        FordTable4Problem.F4_I3.with_n_iterations(14),
        FordTable4Problem.F5_I1.with_n_iterations(
            12,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation="the solve stops one iteration early, on an iterate whose |f(x)| is 0.35 times Ford's limit on "
            "|f(x)|",
        ),
        FordTable4Problem.F5_I2.with_n_iterations(7),
        FordTable4Problem.F5_I3.with_n_iterations(
            17,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=_REACHES_ZERO_ONE_ITERATION_EARLY,
        ),
    ],
    FordVariant.METHOD_4: [
        FordTable4Problem.F1_I1.with_n_iterations(8),
        FordTable4Problem.F1_I2.with_n_iterations(10),
        FordTable4Problem.F1_I3.with_n_iterations(15),
        FordTable4Problem.F2_I1.with_n_iterations(7),
        FordTable4Problem.F2_I2.with_n_iterations(17),
        FordTable4Problem.F2_I3.with_n_iterations(59),
        FordTable4Problem.F3_I1.with_n_iterations(6),
        FordTable4Problem.F3_I2.with_n_iterations(12),
        # `with_n_iterations` cannot leave a count unchecked, but `with_n_fevals` can, with ``deviation=None``; so this
        # row gives Ford's 19 iterations as an evaluation count, adding the 2 evaluations at the interval bounds.
        FordTable4Problem.F3_I3.with_n_fevals(
            19 + 2,
            deviation=None,
            reason="the cause is unknown",
            observation="the solve takes 13 iterations, in float64 and in arithmetic of up to 113 bits; Methods 1 "
            "and 3 reproduce their counts on this problem",
        ),
        FordTable4Problem.F4_I1.with_n_iterations(10),
        FordTable4Problem.F4_I2.with_n_iterations(12),
        FordTable4Problem.F4_I3.with_n_iterations(13),
        FordTable4Problem.F5_I1.with_n_iterations(10),
        FordTable4Problem.F5_I2.with_n_iterations(13),
        FordTable4Problem.F5_I3.with_n_iterations(
            15,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=_REACHES_ZERO_ONE_ITERATION_EARLY,
        ),
    ],
}
