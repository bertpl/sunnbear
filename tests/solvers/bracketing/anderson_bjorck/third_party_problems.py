"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`AndersonBjorck`."""

from tests.solvers.paper_problems.ford import FordTable4Problem

# Ford prints 4 rows as "200+": more than 200 iterations.
FORD_TABLE_4 = [
    FordTable4Problem.F1_I1.with_n_iterations(5),
    FordTable4Problem.F1_I2.with_n_iterations(5),
    FordTable4Problem.F1_I3.with_n_iterations(7),
    FordTable4Problem.F2_I1.with_n_iterations(7),
    FordTable4Problem.F2_I2.with_n_iterations(12),
    FordTable4Problem.F2_I3.with_n_iterations(45),
    FordTable4Problem.F3_I1.with_n_iterations(5),
    FordTable4Problem.F3_I2.with_n_iterations(18),
    FordTable4Problem.F3_I3.with_n_iterations_above(200),
    FordTable4Problem.F4_I1.with_n_iterations(11),
    FordTable4Problem.F4_I2.with_n_iterations(43),
    FordTable4Problem.F4_I3.with_n_iterations_above(200),
    FordTable4Problem.F5_I1.with_n_iterations(18),
    FordTable4Problem.F5_I2.with_n_iterations_above(200),
    FordTable4Problem.F5_I3.with_n_iterations_above(200),
]
