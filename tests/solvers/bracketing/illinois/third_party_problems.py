"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`Illinois`."""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.ford import FordTable4Problem

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
