"""This module holds the published results of Algorithm 748 on the Alefeld-Potra-Shi test problems, for the tests of
`TOMS748Paper`: `TABLES_IV_TO_VI_BY_K`, the evaluation counts of the paper's Tables IV to VI, keyed by ``k``, which
selects Algorithm 4.1 (``k = 1``) or 4.2 (``k = 2``).
"""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.alefeld_potra_shi import AlefeldPotraShiTablesIVToVIProblem

_OVERFLOW_DEVIATION_REASON = (
    "the function is 0 on an interval around its root at 0, where exp(1 / x^2) overflows, so the count depends on "
    "where the platform's exp overflows; the paper's Section 6 states that how this function is coded changes the "
    "results"
)
_POLE_ROUNDING_DEVIATION_REASON = (
    "the count depends on the rounding of f, which reaches about 2e27 in magnitude at the interval bounds next to its "
    "poles: on macOS, the solve takes 13 evaluations with the 20 terms of f summed from i = 1 up, as the problem "
    "defines f, and 15, the paper's count, with them summed from i = 20 down"
)
# `TABLES_IV_TO_VI_BY_K` maps ``k`` to the problems of the paper's Tables IV to VI, each with the paper's evaluation
# count for that ``k``, which counts the 2 evaluations at the interval bounds.
TABLES_IV_TO_VI_BY_K = {
    1: [
        AlefeldPotraShiTablesIVToVIProblem.P26_N1.with_n_fevals(28, deviation=None, reason=_OVERFLOW_DEVIATION_REASON),
        AlefeldPotraShiTablesIVToVIProblem.P13_N1.with_n_fevals(
            25,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation="the solve ends on an ipzero step that lands exactly on the root 0, where f is exactly 0",
        ),
        AlefeldPotraShiTablesIVToVIProblem.P27_N10.with_n_fevals(20),
        AlefeldPotraShiTablesIVToVIProblem.P27_N30.with_n_fevals(20),
        AlefeldPotraShiTablesIVToVIProblem.P28_N30.with_n_fevals(29),
        AlefeldPotraShiTablesIVToVIProblem.P28_N500.with_n_fevals(35),
        AlefeldPotraShiTablesIVToVIProblem.P1_N1.with_n_fevals(10),
        AlefeldPotraShiTablesIVToVIProblem.P3_N1.with_n_fevals(15, deviation=2, reason=_POLE_ROUNDING_DEVIATION_REASON),
        AlefeldPotraShiTablesIVToVIProblem.P16_N4.with_n_fevals(12),
        AlefeldPotraShiTablesIVToVIProblem.P18_N1.with_n_fevals(11),
        AlefeldPotraShiTablesIVToVIProblem.P19_N20.with_n_fevals(12),
        AlefeldPotraShiTablesIVToVIProblem.P20_N10.with_n_fevals(7),
        AlefeldPotraShiTablesIVToVIProblem.P21_N10.with_n_fevals(12),
        AlefeldPotraShiTablesIVToVIProblem.P22_N1.with_n_fevals(11),
        AlefeldPotraShiTablesIVToVIProblem.P23_N5.with_n_fevals(12),
        AlefeldPotraShiTablesIVToVIProblem.P24_N20.with_n_fevals(17),
        AlefeldPotraShiTablesIVToVIProblem.P25_N3.with_n_fevals(6),
    ],
    2: [
        AlefeldPotraShiTablesIVToVIProblem.P26_N1.with_n_fevals(29, deviation=None, reason=_OVERFLOW_DEVIATION_REASON),
        AlefeldPotraShiTablesIVToVIProblem.P13_N1.with_n_fevals(24),
        AlefeldPotraShiTablesIVToVIProblem.P27_N10.with_n_fevals(19),
        AlefeldPotraShiTablesIVToVIProblem.P27_N30.with_n_fevals(19),
        AlefeldPotraShiTablesIVToVIProblem.P28_N30.with_n_fevals(
            31,
            deviation=1,
            reason=UNSTATED_RUN_DETAILS,
            observation=(
                "the solve's last x-value is a step that the margin of section 6 moves to 2*delta inside the interval, "
                "which leaves a new interval 2*delta wide: 0.7 times the width 2*tole(a, b) of the termination test"
            ),
        ),
        AlefeldPotraShiTablesIVToVIProblem.P28_N500.with_n_fevals(35),
        AlefeldPotraShiTablesIVToVIProblem.P1_N1.with_n_fevals(10),
        AlefeldPotraShiTablesIVToVIProblem.P3_N1.with_n_fevals(11),
        AlefeldPotraShiTablesIVToVIProblem.P16_N4.with_n_fevals(13),
        AlefeldPotraShiTablesIVToVIProblem.P18_N1.with_n_fevals(10),
        AlefeldPotraShiTablesIVToVIProblem.P19_N20.with_n_fevals(11),
        AlefeldPotraShiTablesIVToVIProblem.P20_N10.with_n_fevals(7),
        AlefeldPotraShiTablesIVToVIProblem.P21_N10.with_n_fevals(11),
        AlefeldPotraShiTablesIVToVIProblem.P22_N1.with_n_fevals(9),
        AlefeldPotraShiTablesIVToVIProblem.P23_N5.with_n_fevals(9),
        AlefeldPotraShiTablesIVToVIProblem.P24_N20.with_n_fevals(18),
        AlefeldPotraShiTablesIVToVIProblem.P25_N3.with_n_fevals(5),
    ],
}
