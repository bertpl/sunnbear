"""This module holds `TABLE_2`, the cases of Table 2 of Chandrupatla's paper, with the paper's evaluation counts
for its method."""

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import CHANDRUPATLA_BASIC_LISTING_FUNCTIONS

# Each row of the paper's Table 2 holds the function number, the 2 interval bounds and the evaluation count of the
# paper's method.
# The functions are those of the paper's BASIC listing, which produced the table.
TABLE_2 = [
    PaperProblem(
        name=f"{row['number']}[{row['a']:g},{row['b']:g}]",
        f=CHANDRUPATLA_BASIC_LISTING_FUNCTIONS[row["number"]],
        a=float(row["a"]),
        b=float(row["b"]),
        n_fevals=row["n_fevals"],
    )
    for row in [
        {"number": 1, "a": 2, "b": 3, "n_fevals": 7},
        {"number": 1, "a": 1, "b": 10, "n_fevals": 11},
        {"number": 1, "a": 1, "b": 100, "n_fevals": 14},
        {"number": 1, "a": -1e4, "b": 1e4, "n_fevals": 23},
        {"number": 1, "a": -1e10, "b": 1e10, "n_fevals": 43},
        {"number": 2, "a": 0.5, "b": 1.51, "n_fevals": 8},
        {"number": 2, "a": 1e-4, "b": 1e4, "n_fevals": 22},
        {"number": 2, "a": 1e-6, "b": 1e6, "n_fevals": 28},
        {"number": 2, "a": 1e-10, "b": 1e10, "n_fevals": 41},
        {"number": 2, "a": 1e-12, "b": 1e12, "n_fevals": 48},
        {"number": 3, "a": 0, "b": 5, "n_fevals": 21},
        {"number": 3, "a": -10, "b": 10, "n_fevals": 23},
        {"number": 3, "a": -1e4, "b": 1e4, "n_fevals": 36},
        {"number": 3, "a": -1e6, "b": 1e6, "n_fevals": 45},
        {"number": 3, "a": -1e10, "b": 1e10, "n_fevals": 55},
        {"number": 4, "a": 0, "b": 5, "n_fevals": 21},
        {"number": 4, "a": -10, "b": 10, "n_fevals": 23},
        {"number": 4, "a": -1e4, "b": 1e4, "n_fevals": 33},
        {"number": 4, "a": -1e6, "b": 1e6, "n_fevals": 43},
        {"number": 4, "a": -1e10, "b": 1e10, "n_fevals": 54},
        {"number": 5, "a": -1, "b": 4, "n_fevals": 21},
        {"number": 5, "a": -2, "b": 5, "n_fevals": 22},
        {"number": 5, "a": -1, "b": 10, "n_fevals": 23},
        {"number": 5, "a": -5, "b": 50, "n_fevals": 25},
        {"number": 5, "a": -10, "b": 100, "n_fevals": 26},
        {"number": 6, "a": -1, "b": 4, "n_fevals": 21},
        {"number": 6, "a": -2, "b": 5, "n_fevals": 22},
        {"number": 6, "a": -1, "b": 10, "n_fevals": 23},
        {"number": 6, "a": -5, "b": 50, "n_fevals": 25},
        {"number": 6, "a": -10, "b": 100, "n_fevals": 26},
        {"number": 7, "a": -1, "b": 4, "n_fevals": 8},
        {"number": 7, "a": -2, "b": 5, "n_fevals": 8},
        {"number": 7, "a": -1, "b": 10, "n_fevals": 11},
        {"number": 7, "a": -5, "b": 50, "n_fevals": 18},
        {"number": 7, "a": -10, "b": 100, "n_fevals": 19},
        {"number": 8, "a": 2e-4, "b": 2, "n_fevals": 9},
        {"number": 8, "a": 2e-4, "b": 3, "n_fevals": 10},
        {"number": 8, "a": 2e-4, "b": 9, "n_fevals": 11},
        {"number": 8, "a": 2e-4, "b": 27, "n_fevals": 12},
        {"number": 8, "a": 2e-4, "b": 81, "n_fevals": 14},
        {"number": 9, "a": 2e-4, "b": 1, "n_fevals": 7},
        {"number": 9, "a": 2e-4, "b": 3, "n_fevals": 8},
        {"number": 9, "a": 2e-4, "b": 9, "n_fevals": 10},
        {"number": 9, "a": 2e-4, "b": 27, "n_fevals": 11},
        {"number": 9, "a": 2e-4, "b": 81, "n_fevals": 13},
    ]
]
