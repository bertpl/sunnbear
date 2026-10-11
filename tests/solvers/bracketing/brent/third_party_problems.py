"""This module holds third parties' test problems for Brent's method, each with the published count for `Brent`:

- `CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES`: the column "Brent's" of Table 2 of Chandrupatla (1997);
- `ALEFELD_POTRA_SHI_TABLES_IV_TO_VI`: the column "BR" of Tables IV to VI of Alefeld, Potra and Shi (1995);
- `ANDERSON_BJORCK_EXAMPLES_1_TO_7`: the column "Brent" of Examples 1 to 7 of Anderson and Björck (1973), in single
  precision.
"""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.alefeld_potra_shi import AlefeldPotraShiTablesIVToVIProblem
from tests.solvers.paper_problems.anderson_bjorck import AndersonBjorckExampleProblem
from tests.solvers.paper_problems.chandrupatla import ChandrupatlaTable2Problem

# Each pair holds a problem of Chandrupatla's Table 2 with the evaluation count of Brent's method, and the number of
# times that the method switches to bisection, which the table prints in parentheses after that count.
CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES = [
    (ChandrupatlaTable2Problem.F1_I1.with_n_fevals(7), 0),
    (ChandrupatlaTable2Problem.F1_I2.with_n_fevals(13), 2),
    (ChandrupatlaTable2Problem.F1_I3.with_n_fevals(14), 2),
    (ChandrupatlaTable2Problem.F1_I4.with_n_fevals(34), 13),
    (ChandrupatlaTable2Problem.F1_I5.with_n_fevals(74), 34),
    (ChandrupatlaTable2Problem.F2_I1.with_n_fevals(9), 1),
    (ChandrupatlaTable2Problem.F2_I2.with_n_fevals(23), 14),
    (ChandrupatlaTable2Problem.F2_I3.with_n_fevals(28), 20),
    (ChandrupatlaTable2Problem.F2_I4.with_n_fevals(43), 33),
    (ChandrupatlaTable2Problem.F2_I5.with_n_fevals(49), 40),
    (ChandrupatlaTable2Problem.F3_I1.with_n_fevals(49), 13),
    (ChandrupatlaTable2Problem.F3_I2.with_n_fevals(63), 15),
    (ChandrupatlaTable2Problem.F3_I3.with_n_fevals(86), 26),
    (ChandrupatlaTable2Problem.F3_I4.with_n_fevals(101), 32),
    (ChandrupatlaTable2Problem.F3_I5.with_n_fevals(101), 32),
    (ChandrupatlaTable2Problem.F4_I1.with_n_fevals(50), 13),
    (ChandrupatlaTable2Problem.F4_I2.with_n_fevals(50), 13),
    (ChandrupatlaTable2Problem.F4_I3.with_n_fevals(84), 24),
    (ChandrupatlaTable2Problem.F4_I4.with_n_fevals(105), 31),
    (ChandrupatlaTable2Problem.F4_I5.with_n_fevals(146), 46),
    (ChandrupatlaTable2Problem.F5_I1.with_n_fevals(53), 15),
    (ChandrupatlaTable2Problem.F5_I2.with_n_fevals(54), 15),
    (ChandrupatlaTable2Problem.F5_I3.with_n_fevals(58), 17),
    (ChandrupatlaTable2Problem.F5_I4.with_n_fevals(64), 19),
    (ChandrupatlaTable2Problem.F5_I5.with_n_fevals(66), 19),
    (ChandrupatlaTable2Problem.F6_I1.with_n_fevals(53), 16),
    (ChandrupatlaTable2Problem.F6_I2.with_n_fevals(56), 17),
    (ChandrupatlaTable2Problem.F6_I3.with_n_fevals(59), 18),
    (ChandrupatlaTable2Problem.F6_I4.with_n_fevals(66), 20),
    (ChandrupatlaTable2Problem.F6_I5.with_n_fevals(63), 19),
    (ChandrupatlaTable2Problem.F7_I1.with_n_fevals(18), 5),
    (ChandrupatlaTable2Problem.F7_I2.with_n_fevals(21), 6),
    (ChandrupatlaTable2Problem.F7_I3.with_n_fevals(24), 7),
    (ChandrupatlaTable2Problem.F7_I4.with_n_fevals(27), 8),
    (ChandrupatlaTable2Problem.F7_I5.with_n_fevals(33), 10),
    (ChandrupatlaTable2Problem.F8_I1.with_n_fevals(9), 1),
    (ChandrupatlaTable2Problem.F8_I2.with_n_fevals(11), 2),
    (ChandrupatlaTable2Problem.F8_I3.with_n_fevals(12), 3),
    (ChandrupatlaTable2Problem.F8_I4.with_n_fevals(14), 5),
    (ChandrupatlaTable2Problem.F8_I5.with_n_fevals(16), 7),
    (ChandrupatlaTable2Problem.F9_I1.with_n_fevals(7), 0),
    (ChandrupatlaTable2Problem.F9_I2.with_n_fevals(9), 1),
    (ChandrupatlaTable2Problem.F9_I3.with_n_fevals(14), 3),
    (ChandrupatlaTable2Problem.F9_I4.with_n_fevals(18), 4),
    (ChandrupatlaTable2Problem.F9_I5.with_n_fevals(19), 5),
]

# The column "BR" of Alefeld, Potra and Shi's Tables IV to VI counts the 2 evaluations at the interval bounds.
ALEFELD_POTRA_SHI_TABLES_IV_TO_VI = [
    AlefeldPotraShiTablesIVToVIProblem.P26_N1.with_n_fevals(
        23,
        deviation=None,
        reason=(
            "the function underflows to 0 on an interval around its root at 0, so the count depends on where the "
            "platform's exp underflows; the paper's Section 6 states that how this function is coded changes the "
            "results"
        ),
    ),
    AlefeldPotraShiTablesIVToVIProblem.P13_N1.with_n_fevals(19),
    AlefeldPotraShiTablesIVToVIProblem.P27_N10.with_n_fevals(21),
    AlefeldPotraShiTablesIVToVIProblem.P27_N30.with_n_fevals(21),
    AlefeldPotraShiTablesIVToVIProblem.P28_N30.with_n_fevals(36),
    AlefeldPotraShiTablesIVToVIProblem.P28_N500.with_n_fevals(39),
    AlefeldPotraShiTablesIVToVIProblem.P1_N1.with_n_fevals(9),
    AlefeldPotraShiTablesIVToVIProblem.P3_N1.with_n_fevals(10),
    AlefeldPotraShiTablesIVToVIProblem.P16_N4.with_n_fevals(15),
    AlefeldPotraShiTablesIVToVIProblem.P18_N1.with_n_fevals(10),
    AlefeldPotraShiTablesIVToVIProblem.P19_N20.with_n_fevals(13),
    AlefeldPotraShiTablesIVToVIProblem.P20_N10.with_n_fevals(9),
    AlefeldPotraShiTablesIVToVIProblem.P21_N10.with_n_fevals(11),
    AlefeldPotraShiTablesIVToVIProblem.P22_N1.with_n_fevals(10),
    AlefeldPotraShiTablesIVToVIProblem.P23_N5.with_n_fevals(9),
    AlefeldPotraShiTablesIVToVIProblem.P24_N20.with_n_fevals(14),
    AlefeldPotraShiTablesIVToVIProblem.P25_N3.with_n_fevals(10),
]

# The column "Brent" of Anderson and Björck's Examples 1 to 7 gives the iteration counts of the paper's runs in single
# precision; Brent's method evaluates once per iteration.
ANDERSON_BJORCK_EXAMPLES_1_TO_7 = [
    AndersonBjorckExampleProblem.EX1.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX2_N1.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX2_N5.with_n_iterations(
        8,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration fewer",
    ),
    AndersonBjorckExampleProblem.EX2_N15.with_n_iterations(9),
    AndersonBjorckExampleProblem.EX2_N20.with_n_iterations(9),
    AndersonBjorckExampleProblem.EX3_N2.with_n_iterations(7),
    AndersonBjorckExampleProblem.EX3_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX3_N15.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX3_N20.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX4_N2.with_n_iterations(1),
    AndersonBjorckExampleProblem.EX4_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX4_N15.with_n_iterations(8),
    AndersonBjorckExampleProblem.EX4_N20.with_n_iterations(10),
    AndersonBjorckExampleProblem.EX5_N2.with_n_iterations(
        8,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration fewer",
    ),
    AndersonBjorckExampleProblem.EX5_N5.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX5_N15.with_n_iterations(4),
    AndersonBjorckExampleProblem.EX5_N20.with_n_iterations(4),
    AndersonBjorckExampleProblem.EX6_N1.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX6_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX6_N10.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX6_N15.with_n_iterations(9),
    AndersonBjorckExampleProblem.EX6_N20.with_n_iterations(10),
    AndersonBjorckExampleProblem.EX7_N2.with_n_iterations(
        3,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve reaches f(x) == 0 one iteration early",
    ),
    AndersonBjorckExampleProblem.EX7_N5.with_n_iterations(10),
    AndersonBjorckExampleProblem.EX7_N15.with_n_iterations(
        9,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration more",
    ),
    AndersonBjorckExampleProblem.EX7_N20.with_n_iterations(11),
]
