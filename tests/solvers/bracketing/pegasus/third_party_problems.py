"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`Pegasus`."""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.ford import FordTable4Problem

FORD_TABLE_4 = [
    FordTable4Problem.F1_I1.with_n_iterations(6),
    FordTable4Problem.F1_I2.with_n_iterations(10),
    FordTable4Problem.F1_I3.with_n_iterations(18),
    FordTable4Problem.F2_I1.with_n_iterations(7),
    FordTable4Problem.F2_I2.with_n_iterations(14),
    FordTable4Problem.F2_I3.with_n_iterations(103),
    FordTable4Problem.F3_I1.with_n_iterations(5),
    FordTable4Problem.F3_I2.with_n_iterations(27),
    FordTable4Problem.F3_I3.with_n_iterations(42),
    FordTable4Problem.F4_I1.with_n_iterations(
        10,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve reaches f(x) == 0 one iteration early",
    ),
    FordTable4Problem.F4_I2.with_n_iterations(14),
    FordTable4Problem.F4_I3.with_n_iterations(31),
    FordTable4Problem.F5_I1.with_n_iterations(
        14,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve reaches f(x) == 0 one iteration early",
    ),
    FordTable4Problem.F5_I2.with_n_iterations(
        26,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve reaches f(x) == 0 one iteration early",
    ),
    FordTable4Problem.F5_I3.with_n_iterations(46),
]
