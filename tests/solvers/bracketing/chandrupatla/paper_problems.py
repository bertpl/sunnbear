"""This module holds `TABLE_2`, the cases of Table 2 of Chandrupatla's paper, with the paper's evaluation counts
for its method, and `TABLE_2_WITH_N_BISECTION_SWITCHES`, which pairs each case with the number of times that the
paper's method switches to bisection on it."""

from tests.solvers.paper_problems.chandrupatla import ChandrupatlaTable2Problem

# Each pair holds a problem of the paper's Table 2 with the evaluation count of the paper's method, and the number of
# times that the method switches to bisection, which the table prints in parentheses after that count.
TABLE_2_WITH_N_BISECTION_SWITCHES = [
    (ChandrupatlaTable2Problem.F1_I1.with_n_fevals(7), 0),
    (ChandrupatlaTable2Problem.F1_I2.with_n_fevals(11), 4),
    (ChandrupatlaTable2Problem.F1_I3.with_n_fevals(14), 7),
    (ChandrupatlaTable2Problem.F1_I4.with_n_fevals(23), 14),
    (ChandrupatlaTable2Problem.F1_I5.with_n_fevals(43), 34),
    (ChandrupatlaTable2Problem.F2_I1.with_n_fevals(8), 2),
    (ChandrupatlaTable2Problem.F2_I2.with_n_fevals(22), 15),
    (ChandrupatlaTable2Problem.F2_I3.with_n_fevals(28), 21),
    (ChandrupatlaTable2Problem.F2_I4.with_n_fevals(41), 35),
    (ChandrupatlaTable2Problem.F2_I5.with_n_fevals(48), 41),
    (ChandrupatlaTable2Problem.F3_I1.with_n_fevals(21), 18),
    (ChandrupatlaTable2Problem.F3_I2.with_n_fevals(23), 20),
    (ChandrupatlaTable2Problem.F3_I3.with_n_fevals(36), 30),
    (ChandrupatlaTable2Problem.F3_I4.with_n_fevals(45), 37),
    (ChandrupatlaTable2Problem.F3_I5.with_n_fevals(55), 49),
    (ChandrupatlaTable2Problem.F4_I1.with_n_fevals(21), 18),
    (ChandrupatlaTable2Problem.F4_I2.with_n_fevals(23), 20),
    (ChandrupatlaTable2Problem.F4_I3.with_n_fevals(33), 28),
    (ChandrupatlaTable2Problem.F4_I4.with_n_fevals(43), 37),
    (ChandrupatlaTable2Problem.F4_I5.with_n_fevals(54), 48),
    (ChandrupatlaTable2Problem.F5_I1.with_n_fevals(21), 18),
    (ChandrupatlaTable2Problem.F5_I2.with_n_fevals(22), 19),
    (ChandrupatlaTable2Problem.F5_I3.with_n_fevals(23), 20),
    (ChandrupatlaTable2Problem.F5_I4.with_n_fevals(25), 22),
    (ChandrupatlaTable2Problem.F5_I5.with_n_fevals(26), 23),
    (ChandrupatlaTable2Problem.F6_I1.with_n_fevals(21), 18),
    (ChandrupatlaTable2Problem.F6_I2.with_n_fevals(22), 19),
    (ChandrupatlaTable2Problem.F6_I3.with_n_fevals(23), 20),
    (ChandrupatlaTable2Problem.F6_I4.with_n_fevals(25), 22),
    (ChandrupatlaTable2Problem.F6_I5.with_n_fevals(26), 23),
    (ChandrupatlaTable2Problem.F7_I1.with_n_fevals(8), 3),
    (ChandrupatlaTable2Problem.F7_I2.with_n_fevals(8), 3),
    (ChandrupatlaTable2Problem.F7_I3.with_n_fevals(11), 5),
    (ChandrupatlaTable2Problem.F7_I4.with_n_fevals(18), 9),
    (ChandrupatlaTable2Problem.F7_I5.with_n_fevals(19), 9),
    (ChandrupatlaTable2Problem.F8_I1.with_n_fevals(9), 2),
    (ChandrupatlaTable2Problem.F8_I2.with_n_fevals(10), 3),
    (ChandrupatlaTable2Problem.F8_I3.with_n_fevals(11), 4),
    (ChandrupatlaTable2Problem.F8_I4.with_n_fevals(12), 6),
    (ChandrupatlaTable2Problem.F8_I5.with_n_fevals(14), 7),
    (ChandrupatlaTable2Problem.F9_I1.with_n_fevals(7), 0),
    (ChandrupatlaTable2Problem.F9_I2.with_n_fevals(8), 1),
    (ChandrupatlaTable2Problem.F9_I3.with_n_fevals(10), 3),
    (ChandrupatlaTable2Problem.F9_I4.with_n_fevals(11), 4),
    (ChandrupatlaTable2Problem.F9_I5.with_n_fevals(13), 6),
]

TABLE_2 = [problem for problem, _ in TABLE_2_WITH_N_BISECTION_SWITCHES]
