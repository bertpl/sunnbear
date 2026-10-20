"""This module holds third parties' test problems for Brent's method, each with the published count for `Brent`:

- `CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES`: the column "Brent's" of Table 2 of Chandrupatla (1997);
- `ALEFELD_POTRA_SHI_TABLES_IV_TO_VI`: the column "BR" of Tables IV to VI of Alefeld, Potra and Shi (1995);
- `ANDERSON_BJORCK_EXAMPLES_1_TO_7`: the column "Brent" of Examples 1 to 7 of Anderson and Björck (1973), in single
  precision;
- `GANCHOVSKI_ET_AL_TABLE_2`: the column "Bre" of Table 2 of Ganchovski et al. (2026), with Brent's root in the paper's
  supplementary results;
- `BUS_DEKKER_TABLES_I_TO_IV`: the column "B" of Tables I to IV of Bus and Dekker (1975).
"""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.alefeld_potra_shi import AlefeldPotraShiTablesIVToVIProblem
from tests.solvers.paper_problems.anderson_bjorck import AndersonBjorckExampleProblem
from tests.solvers.paper_problems.bus_dekker import BusDekkerTablesIToIVProblem
from tests.solvers.paper_problems.chandrupatla import ChandrupatlaTable2Problem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem

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
            "the function is 0 on an interval around its root at 0, where exp(1 / x^2) overflows, so the count "
            "depends on where the platform's exp overflows; the paper's Section 6 states that how this function is "
            "coded changes the results"
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

GANCHOVSKI_ET_AL_TABLE_2 = [
    GanchovskiEtAlTable2Problem.F01.with_n_fevals_and_root(10, root=1.0),
    GanchovskiEtAlTable2Problem.F02.with_n_fevals_and_root(13, root=0.399422291710968),
    GanchovskiEtAlTable2Problem.F03.with_n_fevals_and_root(12, root=0.804133097503664),
    GanchovskiEtAlTable2Problem.F04.with_n_fevals_and_root(10, root=-1.0),
    GanchovskiEtAlTable2Problem.F05.with_n_fevals_and_root(8, root=2.09455148154232),
    GanchovskiEtAlTable2Problem.F06.with_n_fevals_and_root(10, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F07.with_n_fevals_and_root(12, root=0.0693140886870234),
    GanchovskiEtAlTable2Problem.F08.with_n_fevals_and_root(12, root=0.0346573590208538),
    GanchovskiEtAlTable2Problem.F09.with_n_fevals_and_root(10, root=0.109611796797792),
    GanchovskiEtAlTable2Problem.F10.with_n_fevals_and_root(10, root=0.0524786034368101),
    GanchovskiEtAlTable2Problem.F11.with_n_fevals_and_root(9, root=0.0256237476199884),
    GanchovskiEtAlTable2Problem.F12.with_n_fevals_and_root(9, root=0.345954815848242),
    GanchovskiEtAlTable2Problem.F13.with_n_fevals_and_root(10, root=0.245122333753307),
    GanchovskiEtAlTable2Problem.F14.with_n_fevals_and_root(13, root=0.16492095727644),
    GanchovskiEtAlTable2Problem.F15.with_n_fevals_and_root(8, root=0.00361710817890406),
    GanchovskiEtAlTable2Problem.F16.with_n_fevals_and_root(7, root=0.000151471334783891),
    GanchovskiEtAlTable2Problem.F17.with_n_fevals_and_root(7, root=7.66859512218533e-06),
    GanchovskiEtAlTable2Problem.F18.with_n_fevals_and_root(9, root=0.516153518757933),
    GanchovskiEtAlTable2Problem.F19.with_n_fevals_and_root(9, root=0.539522226908413),
    GanchovskiEtAlTable2Problem.F20.with_n_fevals_and_root(13, root=0.552704666678487),
    GanchovskiEtAlTable2Problem.F21.with_n_fevals_and_root(11, root=0.409992017989137),
    GanchovskiEtAlTable2Problem.F22.with_n_fevals_and_root(10, root=0.452509145577641),
    GanchovskiEtAlTable2Problem.F23.with_n_fevals_and_root(10, root=0.475626848596062),
    GanchovskiEtAlTable2Problem.F24.with_n_fevals_and_root(137, root=2.99999999999999),
    GanchovskiEtAlTable2Problem.F25.with_n_fevals_and_root(118, root=4.0),
    GanchovskiEtAlTable2Problem.F26.with_n_fevals_and_root(137, root=2.47457678736982),
    GanchovskiEtAlTable2Problem.F27.with_n_fevals_and_root(31, root=1.88914310822898),
    GanchovskiEtAlTable2Problem.F28.with_n_fevals_and_root(131, root=7.14299999999999),
    GanchovskiEtAlTable2Problem.F29.with_n_fevals_and_root(30, root=2.99980076330914),
    GanchovskiEtAlTable2Problem.F30.with_n_fevals_and_root(14, root=4.26716830454212),
    GanchovskiEtAlTable2Problem.F31.with_n_fevals_and_root(12, root=0.31830988618379),
    GanchovskiEtAlTable2Problem.F32.with_n_fevals_and_root(13, root=1.32581766366803),
    GanchovskiEtAlTable2Problem.F33.with_n_fevals_and_root(15, root=0.865474033101614),
    GanchovskiEtAlTable2Problem.F34.with_n_fevals_and_root(
        10,
        root=0.73908513321516,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=(
            "the solve takes 1 evaluation fewer; with the cos of macOS's C library in place of a correctly rounded "
            "cos, it takes the table's 10"
        ),
    ),
    GanchovskiEtAlTable2Problem.F35.with_n_fevals_and_root(11, root=0.656666666666666),
    GanchovskiEtAlTable2Problem.F36.with_n_fevals_and_root(44, root=0.666666666666665),
    GanchovskiEtAlTable2Problem.F37.with_n_fevals_and_root(31, root=0.777777777777777),
    GanchovskiEtAlTable2Problem.F38.with_n_fevals_and_root(53, root=0.333333333333337),
    GanchovskiEtAlTable2Problem.F39.with_n_fevals_and_root(83, root=0.333333333333332),
    GanchovskiEtAlTable2Problem.F40.with_n_fevals_and_root(55, root=0.666666666666657),
    GanchovskiEtAlTable2Problem.F41.with_n_fevals_and_root(13, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F42.with_n_fevals_and_root(10, root=3.0),
    GanchovskiEtAlTable2Problem.F43.with_n_fevals_and_root(124, root=-1.76712656679895e-15),
    # `Brent`'s roots on f44 and f45, x^5 and x^7, lie near 1e-15, close to their true root at 0, and differ from the
    # published roots by about 1e-27; they match only to a relative 1e-12, not to `GANCHOVSKI_ET_AL_ROOT_REL_TOL`.
    GanchovskiEtAlTable2Problem.F44.with_n_fevals_and_root(127, root=2.45000610953973e-15, root_rel_tol=1e-12),
    GanchovskiEtAlTable2Problem.F45.with_n_fevals_and_root(135, root=-1.15436487217852e-15, root_rel_tol=1e-12),
    GanchovskiEtAlTable2Problem.F46.with_n_fevals_and_root(15, root=0.101624392293549),
    GanchovskiEtAlTable2Problem.F47.with_n_fevals_and_root(16, root=0.00773252320061279),
    GanchovskiEtAlTable2Problem.F48.with_n_fevals_and_root(16, root=0.00127630494573559),
    GanchovskiEtAlTable2Problem.F49.with_n_fevals_and_root(11, root=-0.682327803828019),
    GanchovskiEtAlTable2Problem.F50.with_n_fevals_and_root(12, root=-2.10380340273553),
    GanchovskiEtAlTable2Problem.F51.with_n_fevals_and_root(10, root=1.0),
    GanchovskiEtAlTable2Problem.F52.with_n_fevals_and_root(17, root=1.00004083556472),
    GanchovskiEtAlTable2Problem.F53.with_n_fevals_and_root(14, root=1.69681238680975),
    GanchovskiEtAlTable2Problem.F54.with_n_fevals_and_root(8, root=0.523598775598298),
    GanchovskiEtAlTable2Problem.F55.with_n_fevals_and_root(11, root=0.999999999999996),
    GanchovskiEtAlTable2Problem.F56.with_n_fevals_and_root(11, root=2.0),
    GanchovskiEtAlTable2Problem.F57.with_n_fevals_and_root(12, root=3.0),
    GanchovskiEtAlTable2Problem.F58.with_n_fevals_and_root(10, root=1.5574077246549),
    GanchovskiEtAlTable2Problem.F59.with_n_fevals_and_root(13, root=1.25643120862616),
    GanchovskiEtAlTable2Problem.F60.with_n_fevals_and_root(8, root=0.354463104375025),
    GanchovskiEtAlTable2Problem.F61.with_n_fevals_and_root(11, root=1.40449164821534),
    GanchovskiEtAlTable2Problem.F62.with_n_fevals_and_root(9, root=1.89549426703398),
    GanchovskiEtAlTable2Problem.F63.with_n_fevals_and_root(10, root=0.567143290409783),
    GanchovskiEtAlTable2Problem.F64.with_n_fevals_and_root(9, root=0.1),
    GanchovskiEtAlTable2Problem.F65.with_n_fevals_and_root(
        8,
        root=-0.523598775598298,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 evaluation more",
    ),
    GanchovskiEtAlTable2Problem.F66.with_n_fevals_and_root(10, root=-0.843914568649263),
    GanchovskiEtAlTable2Problem.F67.with_n_fevals_and_root(12, root=0.835079042723559),
    GanchovskiEtAlTable2Problem.F68.with_n_fevals_and_root(8, root=0.873568526830231),
    GanchovskiEtAlTable2Problem.F69.with_n_fevals_and_root(10, root=0.11111111111111),
    GanchovskiEtAlTable2Problem.F70.with_n_fevals_and_root(11, root=-0.0370201277078609),
    GanchovskiEtAlTable2Problem.F71.with_n_fevals_and_root(13, root=-0.666666666666663),
    GanchovskiEtAlTable2Problem.F72.with_n_fevals_and_root(139, root=1.00000000199762e-06),
    GanchovskiEtAlTable2Problem.F73.with_n_fevals_and_root(141, root=1.00000000060604e-06),
    GanchovskiEtAlTable2Problem.F74.with_n_fevals_and_root(142, root=0.333333333333334),
    GanchovskiEtAlTable2Problem.F75.with_n_fevals_and_root(66, root=0.333333349861514),
    GanchovskiEtAlTable2Problem.F76.with_n_fevals_and_root(49, root=-0.999999000000004),
    GanchovskiEtAlTable2Problem.F77.with_n_fevals_and_root(53, root=0.0476190476190529),
    GanchovskiEtAlTable2Problem.F78.with_n_fevals_and_root(51, root=-9.83638457885193e-16),
    GanchovskiEtAlTable2Problem.F79.with_n_fevals_and_root(47, root=1.50413845071253e-16),
    GanchovskiEtAlTable2Problem.F80.with_n_fevals_and_root(21, root=-0.0282363589218286),
    GanchovskiEtAlTable2Problem.F81.with_n_fevals_and_root(51, root=-0.99999999999999),
    GanchovskiEtAlTable2Problem.F82.with_n_fevals_and_root(4, root=0.05),
    GanchovskiEtAlTable2Problem.F83.with_n_fevals_and_root(125, root=0.257920792079211),
    GanchovskiEtAlTable2Problem.F84.with_n_fevals_and_root(8, root=3.01250244276146),
    GanchovskiEtAlTable2Problem.F85.with_n_fevals_and_root(12, root=-2.20778314488693),
    GanchovskiEtAlTable2Problem.F86.with_n_fevals_and_root(16, root=0.302804157270694),
    GanchovskiEtAlTable2Problem.F87.with_n_fevals_and_root(12, root=0.98780487804878),
    GanchovskiEtAlTable2Problem.F88.with_n_fevals_and_root(13, root=0.168362173262536),
    GanchovskiEtAlTable2Problem.F89.with_n_fevals_and_root(17, root=-3.63693954875174),
    GanchovskiEtAlTable2Problem.F90.with_n_fevals_and_root(15, root=1.14759628853458),
    GanchovskiEtAlTable2Problem.F91.with_n_fevals_and_root(13, root=0.353913733550918),
    GanchovskiEtAlTable2Problem.F92.with_n_fevals_and_root(24, root=0.1),
]

# The article ran its tables on a CDC Cyber 73, whose floating-point significand has 48 bits. Its column "B" counts the
# 2 evaluations at the interval bounds.
_CYBER_48_BIT_EMULATION_PHRASE = "an emulation of the 48-bit truncating arithmetic of the article's CDC Cyber 73"
BUS_DEKKER_TABLES_I_TO_IV = [
    BusDekkerTablesIToIVProblem.I1.with_n_fevals(
        8,
        deviation=2,
        reason=(
            "cause not known: the solve takes 10 evaluations in float64, in "
            f"{_CYBER_48_BIT_EMULATION_PHRASE}, and in the same emulation with rounding"
        ),
    ),
    BusDekkerTablesIToIVProblem.I2_N1.with_n_fevals(8),
    BusDekkerTablesIToIVProblem.I2_N2.with_n_fevals(
        9,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 evaluation more; in {_CYBER_48_BIT_EMULATION_PHRASE}, it takes the table's 9",
    ),
    BusDekkerTablesIToIVProblem.I2_N3.with_n_fevals(
        10,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 evaluation fewer; in {_CYBER_48_BIT_EMULATION_PHRASE}, it takes the table's 10",
    ),
    BusDekkerTablesIToIVProblem.I2_N4.with_n_fevals(
        10,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 evaluation more; in {_CYBER_48_BIT_EMULATION_PHRASE}, it takes the table's 10",
    ),
    BusDekkerTablesIToIVProblem.I3_N1.with_n_fevals(
        8,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 evaluation more, also in {_CYBER_48_BIT_EMULATION_PHRASE}",
    ),
    BusDekkerTablesIToIVProblem.I3_N5.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I3_N10.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I4_N1.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I4_N5.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I4_N10.with_n_fevals(10),
    BusDekkerTablesIToIVProblem.I5_N1.with_n_fevals(
        9,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 evaluation more; in {_CYBER_48_BIT_EMULATION_PHRASE}, it takes the table's 9",
    ),
    BusDekkerTablesIToIVProblem.I5_N4.with_n_fevals(8),
    BusDekkerTablesIToIVProblem.I5_N8.with_n_fevals(7),
    BusDekkerTablesIToIVProblem.I6_N1.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I6_N5.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.I6_N10.with_n_fevals(9),
    BusDekkerTablesIToIVProblem.II_A1_B0_N3.with_n_fevals(15),
    BusDekkerTablesIToIVProblem.II_A1_B0_N5.with_n_fevals(14),
    BusDekkerTablesIToIVProblem.II_A1_B0_N9.with_n_fevals(16),
    BusDekkerTablesIToIVProblem.II_A1_B0_N19.with_n_fevals(16),
    BusDekkerTablesIToIVProblem.II_A0_B1EM4_N3.with_n_fevals(26),
    BusDekkerTablesIToIVProblem.II_A0_B1EM4_N5.with_n_fevals(27),
    BusDekkerTablesIToIVProblem.II_A0_B1EM4_N9.with_n_fevals(25),
    BusDekkerTablesIToIVProblem.II_A0_B1EM4_N19.with_n_fevals(24),
    BusDekkerTablesIToIVProblem.II_A1_B1EM4_N3.with_n_fevals(14),
    BusDekkerTablesIToIVProblem.II_A1_B1EM4_N5.with_n_fevals(14),
    BusDekkerTablesIToIVProblem.II_A1_B1EM4_N9.with_n_fevals(16),
    BusDekkerTablesIToIVProblem.II_A1_B1EM4_N19.with_n_fevals(16),
    BusDekkerTablesIToIVProblem.III_N3.with_n_fevals(147),
    BusDekkerTablesIToIVProblem.III_N5.with_n_fevals(
        122,
        deviation=None,
        reason=(
            "the count depends on the arithmetic near the multiple root: the solve takes 129 evaluations in float64, "
            f"and 126 in {_CYBER_48_BIT_EMULATION_PHRASE}"
        ),
    ),
    BusDekkerTablesIToIVProblem.III_N7.with_n_fevals(138),
    BusDekkerTablesIToIVProblem.III_N9.with_n_fevals(137),
    BusDekkerTablesIToIVProblem.III_N19.with_n_fevals(
        141,
        deviation=3,
        reason=(
            "the count depends on the arithmetic near the multiple root: the solve takes 138 evaluations in float64, "
            f"and the table's 141 in {_CYBER_48_BIT_EMULATION_PHRASE}"
        ),
    ),
    BusDekkerTablesIToIVProblem.III_N25.with_n_fevals(
        123,
        deviation=None,
        reason=(
            "the count depends on the arithmetic near the multiple root: the solve takes 132 evaluations in float64, "
            f"and 124 in {_CYBER_48_BIT_EMULATION_PHRASE}"
        ),
    ),
    BusDekkerTablesIToIVProblem.IV.with_n_fevals(18),
]
