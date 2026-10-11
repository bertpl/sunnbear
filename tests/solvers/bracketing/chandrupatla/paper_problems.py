"""This module holds `TABLE_2`, the cases of Table 2 of Chandrupatla's paper, with the paper's evaluation counts
for its method, and `TABLE_2_N_BISECTION_SWITCHES`, the paper's bisection-switch counts for the same cases."""

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import CHANDRUPATLA_BASIC_LISTING_FUNCTIONS

# Each row of the paper's Table 2 holds:
# - the function number;
# - the 2 interval bounds;
# - the evaluation count of the paper's method, with its number of bisection switches in parentheses.
_TABLE_2_ROWS = [
    {"number": 1, "a": 2, "b": 3, "n_fevals": 7, "n_bisection_switches": 0},
    {"number": 1, "a": 1, "b": 10, "n_fevals": 11, "n_bisection_switches": 4},
    {"number": 1, "a": 1, "b": 100, "n_fevals": 14, "n_bisection_switches": 7},
    {"number": 1, "a": -1e4, "b": 1e4, "n_fevals": 23, "n_bisection_switches": 14},
    {"number": 1, "a": -1e10, "b": 1e10, "n_fevals": 43, "n_bisection_switches": 34},
    {"number": 2, "a": 0.5, "b": 1.51, "n_fevals": 8, "n_bisection_switches": 2},
    {"number": 2, "a": 1e-4, "b": 1e4, "n_fevals": 22, "n_bisection_switches": 15},
    {"number": 2, "a": 1e-6, "b": 1e6, "n_fevals": 28, "n_bisection_switches": 21},
    {"number": 2, "a": 1e-10, "b": 1e10, "n_fevals": 41, "n_bisection_switches": 35},
    {"number": 2, "a": 1e-12, "b": 1e12, "n_fevals": 48, "n_bisection_switches": 41},
    {"number": 3, "a": 0, "b": 5, "n_fevals": 21, "n_bisection_switches": 18},
    {"number": 3, "a": -10, "b": 10, "n_fevals": 23, "n_bisection_switches": 20},
    {"number": 3, "a": -1e4, "b": 1e4, "n_fevals": 36, "n_bisection_switches": 30},
    {"number": 3, "a": -1e6, "b": 1e6, "n_fevals": 45, "n_bisection_switches": 37},
    {"number": 3, "a": -1e10, "b": 1e10, "n_fevals": 55, "n_bisection_switches": 49},
    {"number": 4, "a": 0, "b": 5, "n_fevals": 21, "n_bisection_switches": 18},
    {"number": 4, "a": -10, "b": 10, "n_fevals": 23, "n_bisection_switches": 20},
    {"number": 4, "a": -1e4, "b": 1e4, "n_fevals": 33, "n_bisection_switches": 28},
    {"number": 4, "a": -1e6, "b": 1e6, "n_fevals": 43, "n_bisection_switches": 37},
    {"number": 4, "a": -1e10, "b": 1e10, "n_fevals": 54, "n_bisection_switches": 48},
    {"number": 5, "a": -1, "b": 4, "n_fevals": 21, "n_bisection_switches": 18},
    {"number": 5, "a": -2, "b": 5, "n_fevals": 22, "n_bisection_switches": 19},
    {"number": 5, "a": -1, "b": 10, "n_fevals": 23, "n_bisection_switches": 20},
    {"number": 5, "a": -5, "b": 50, "n_fevals": 25, "n_bisection_switches": 22},
    {"number": 5, "a": -10, "b": 100, "n_fevals": 26, "n_bisection_switches": 23},
    {"number": 6, "a": -1, "b": 4, "n_fevals": 21, "n_bisection_switches": 18},
    {"number": 6, "a": -2, "b": 5, "n_fevals": 22, "n_bisection_switches": 19},
    {"number": 6, "a": -1, "b": 10, "n_fevals": 23, "n_bisection_switches": 20},
    {"number": 6, "a": -5, "b": 50, "n_fevals": 25, "n_bisection_switches": 22},
    {"number": 6, "a": -10, "b": 100, "n_fevals": 26, "n_bisection_switches": 23},
    {"number": 7, "a": -1, "b": 4, "n_fevals": 8, "n_bisection_switches": 3},
    {"number": 7, "a": -2, "b": 5, "n_fevals": 8, "n_bisection_switches": 3},
    {"number": 7, "a": -1, "b": 10, "n_fevals": 11, "n_bisection_switches": 5},
    {"number": 7, "a": -5, "b": 50, "n_fevals": 18, "n_bisection_switches": 9},
    {"number": 7, "a": -10, "b": 100, "n_fevals": 19, "n_bisection_switches": 9},
    {"number": 8, "a": 2e-4, "b": 2, "n_fevals": 9, "n_bisection_switches": 2},
    {"number": 8, "a": 2e-4, "b": 3, "n_fevals": 10, "n_bisection_switches": 3},
    {"number": 8, "a": 2e-4, "b": 9, "n_fevals": 11, "n_bisection_switches": 4},
    {"number": 8, "a": 2e-4, "b": 27, "n_fevals": 12, "n_bisection_switches": 6},
    {"number": 8, "a": 2e-4, "b": 81, "n_fevals": 14, "n_bisection_switches": 7},
    {"number": 9, "a": 2e-4, "b": 1, "n_fevals": 7, "n_bisection_switches": 0},
    {"number": 9, "a": 2e-4, "b": 3, "n_fevals": 8, "n_bisection_switches": 1},
    {"number": 9, "a": 2e-4, "b": 9, "n_fevals": 10, "n_bisection_switches": 3},
    {"number": 9, "a": 2e-4, "b": 27, "n_fevals": 11, "n_bisection_switches": 4},
    {"number": 9, "a": 2e-4, "b": 81, "n_fevals": 13, "n_bisection_switches": 6},
]

# The functions are those of the paper's BASIC listing, which produced the table.
TABLE_2 = [
    PaperProblem(
        name=f"{row['number']}[{row['a']:g},{row['b']:g}]",
        f=CHANDRUPATLA_BASIC_LISTING_FUNCTIONS[row["number"]],
        a=float(row["a"]),
        b=float(row["b"]),
        n_fevals=row["n_fevals"],
    )
    for row in _TABLE_2_ROWS
]

TABLE_2_N_BISECTION_SWITCHES = {
    problem.name: row["n_bisection_switches"] for problem, row in zip(TABLE_2, _TABLE_2_ROWS, strict=True)
}
