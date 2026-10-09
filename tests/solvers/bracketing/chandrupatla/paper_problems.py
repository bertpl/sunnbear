"""This module holds `TABLE_2`, the cases of Table 2 of Chandrupatla's paper, with the paper's evaluation counts
for its method."""

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import CHANDRUPATLA_BASIC_LISTING_FUNCTIONS

# Each row of the paper's Table 2 holds:
# - the function number;
# - the 2 interval bounds;
# - the evaluation count of the paper's method.
# The functions are those of the paper's BASIC listing, which produced the table.
TABLE_2 = [
    PaperProblem(
        f"{number}[{a:g},{b:g}]", CHANDRUPATLA_BASIC_LISTING_FUNCTIONS[number], float(a), float(b), n_fevals=n_fevals
    )
    for number, a, b, n_fevals in [
        (1, 2, 3, 7),
        (1, 1, 10, 11),
        (1, 1, 100, 14),
        (1, -1e4, 1e4, 23),
        (1, -1e10, 1e10, 43),
        (2, 0.5, 1.51, 8),
        (2, 1e-4, 1e4, 22),
        (2, 1e-6, 1e6, 28),
        (2, 1e-10, 1e10, 41),
        (2, 1e-12, 1e12, 48),
        (3, 0, 5, 21),
        (3, -10, 10, 23),
        (3, -1e4, 1e4, 36),
        (3, -1e6, 1e6, 45),
        (3, -1e10, 1e10, 55),
        (4, 0, 5, 21),
        (4, -10, 10, 23),
        (4, -1e4, 1e4, 33),
        (4, -1e6, 1e6, 43),
        (4, -1e10, 1e10, 54),
        (5, -1, 4, 21),
        (5, -2, 5, 22),
        (5, -1, 10, 23),
        (5, -5, 50, 25),
        (5, -10, 100, 26),
        (6, -1, 4, 21),
        (6, -2, 5, 22),
        (6, -1, 10, 23),
        (6, -5, 50, 25),
        (6, -10, 100, 26),
        (7, -1, 4, 8),
        (7, -2, 5, 8),
        (7, -1, 10, 11),
        (7, -5, 50, 18),
        (7, -10, 100, 19),
        (8, 2e-4, 2, 9),
        (8, 2e-4, 3, 10),
        (8, 2e-4, 9, 11),
        (8, 2e-4, 27, 12),
        (8, 2e-4, 81, 14),
        (9, 2e-4, 1, 7),
        (9, 2e-4, 3, 8),
        (9, 2e-4, 9, 10),
        (9, 2e-4, 27, 11),
        (9, 2e-4, 81, 13),
    ]
]
