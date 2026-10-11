"""This module holds `TABLE_2`, the cases of Table 2 of Chandrupatla's paper, with the paper's evaluation counts
for its method, and `TABLE_2_WITH_N_BISECTION_SWITCHES`, which pairs each case with the number of times that the
paper's method switches to bisection on it."""

from tests.solvers.paper_problems.chandrupatla import chandrupatla_table_2_problems

# `_TABLE_2_ROWS` holds the rows of the paper's Table 2, with the evaluation count of the paper's method, followed in
# the table by the number of times that the method switches to bisection, in parentheses.
_TABLE_2_ROWS = [
    {"name": "1[2,3]", "n_fevals": 7, "n_bisection_switches": 0},
    {"name": "1[1,10]", "n_fevals": 11, "n_bisection_switches": 4},
    {"name": "1[1,100]", "n_fevals": 14, "n_bisection_switches": 7},
    {"name": "1[-10000,10000]", "n_fevals": 23, "n_bisection_switches": 14},
    {"name": "1[-1e+10,1e+10]", "n_fevals": 43, "n_bisection_switches": 34},
    {"name": "2[0.5,1.51]", "n_fevals": 8, "n_bisection_switches": 2},
    {"name": "2[0.0001,10000]", "n_fevals": 22, "n_bisection_switches": 15},
    {"name": "2[1e-06,1e+06]", "n_fevals": 28, "n_bisection_switches": 21},
    {"name": "2[1e-10,1e+10]", "n_fevals": 41, "n_bisection_switches": 35},
    {"name": "2[1e-12,1e+12]", "n_fevals": 48, "n_bisection_switches": 41},
    {"name": "3[0,5]", "n_fevals": 21, "n_bisection_switches": 18},
    {"name": "3[-10,10]", "n_fevals": 23, "n_bisection_switches": 20},
    {"name": "3[-10000,10000]", "n_fevals": 36, "n_bisection_switches": 30},
    {"name": "3[-1e+06,1e+06]", "n_fevals": 45, "n_bisection_switches": 37},
    {"name": "3[-1e+10,1e+10]", "n_fevals": 55, "n_bisection_switches": 49},
    {"name": "4[0,5]", "n_fevals": 21, "n_bisection_switches": 18},
    {"name": "4[-10,10]", "n_fevals": 23, "n_bisection_switches": 20},
    {"name": "4[-10000,10000]", "n_fevals": 33, "n_bisection_switches": 28},
    {"name": "4[-1e+06,1e+06]", "n_fevals": 43, "n_bisection_switches": 37},
    {"name": "4[-1e+10,1e+10]", "n_fevals": 54, "n_bisection_switches": 48},
    {"name": "5[-1,4]", "n_fevals": 21, "n_bisection_switches": 18},
    {"name": "5[-2,5]", "n_fevals": 22, "n_bisection_switches": 19},
    {"name": "5[-1,10]", "n_fevals": 23, "n_bisection_switches": 20},
    {"name": "5[-5,50]", "n_fevals": 25, "n_bisection_switches": 22},
    {"name": "5[-10,100]", "n_fevals": 26, "n_bisection_switches": 23},
    {"name": "6[-1,4]", "n_fevals": 21, "n_bisection_switches": 18},
    {"name": "6[-2,5]", "n_fevals": 22, "n_bisection_switches": 19},
    {"name": "6[-1,10]", "n_fevals": 23, "n_bisection_switches": 20},
    {"name": "6[-5,50]", "n_fevals": 25, "n_bisection_switches": 22},
    {"name": "6[-10,100]", "n_fevals": 26, "n_bisection_switches": 23},
    {"name": "7[-1,4]", "n_fevals": 8, "n_bisection_switches": 3},
    {"name": "7[-2,5]", "n_fevals": 8, "n_bisection_switches": 3},
    {"name": "7[-1,10]", "n_fevals": 11, "n_bisection_switches": 5},
    {"name": "7[-5,50]", "n_fevals": 18, "n_bisection_switches": 9},
    {"name": "7[-10,100]", "n_fevals": 19, "n_bisection_switches": 9},
    {"name": "8[0.0002,2]", "n_fevals": 9, "n_bisection_switches": 2},
    {"name": "8[0.0002,3]", "n_fevals": 10, "n_bisection_switches": 3},
    {"name": "8[0.0002,9]", "n_fevals": 11, "n_bisection_switches": 4},
    {"name": "8[0.0002,27]", "n_fevals": 12, "n_bisection_switches": 6},
    {"name": "8[0.0002,81]", "n_fevals": 14, "n_bisection_switches": 7},
    {"name": "9[0.0002,1]", "n_fevals": 7, "n_bisection_switches": 0},
    {"name": "9[0.0002,3]", "n_fevals": 8, "n_bisection_switches": 1},
    {"name": "9[0.0002,9]", "n_fevals": 10, "n_bisection_switches": 3},
    {"name": "9[0.0002,27]", "n_fevals": 11, "n_bisection_switches": 4},
    {"name": "9[0.0002,81]", "n_fevals": 13, "n_bisection_switches": 6},
]

# Each pair holds a problem of `TABLE_2` and the paper's number of bisection switches on it.
TABLE_2_WITH_N_BISECTION_SWITCHES = chandrupatla_table_2_problems(_TABLE_2_ROWS)

TABLE_2 = [problem for problem, _ in TABLE_2_WITH_N_BISECTION_SWITCHES]
