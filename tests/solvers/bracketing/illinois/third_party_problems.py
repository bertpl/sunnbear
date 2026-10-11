"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`Illinois`."""

from tests.solvers.paper_problems.ford import F_EQUALS_ZERO_DEVIATION_REASON, ford_table_4_problems

# `_FORD_TABLE_4_ROWS` holds the rows of Ford's Table 4, with Ford's iteration counts for `Illinois`.
_FORD_TABLE_4_ROWS = [
    {"name": "1[0.5,2]", "n_iterations": 10},
    {"name": "1[0.2,6]", "n_iterations": 12},
    {"name": "1[0.004,200]", "n_iterations": 21},
    {"name": "2[0.9,1.1]", "n_iterations": 8},
    {"name": "2[0.5,1.5]", "n_iterations": 15},
    {"name": "2[-5,10]", "n_iterations": 70},
    {"name": "3[550,560]", "n_iterations": 7},
    {"name": "3[400,600]", "n_iterations": 29},
    {"name": "3[350,850]", "n_iterations": 44},
    {"name": "4[0,1]", "n_iterations": 9},
    {"name": "4[-0.1,1.5]", "n_iterations": 15},
    {"name": "4[-0.5,2]", "n_iterations": 33},
    {"name": "5[0.035,0.05]", "n_iterations": 14},
    {"name": "5[0.03,0.09]", "n_iterations": 27},
    {"name": "5[0.025,0.5]", "n_iterations": 49},
]

# `_FORD_TABLE_4_DEVIATIONS` maps the name of each row whose count `Illinois` does not reproduce exactly to the
# allowed deviation and its reason.
_FORD_TABLE_4_DEVIATIONS = {
    "2[0.5,1.5]": (
        1,
        "the solve stops on an iterate whose |f(x)| is 0.994 times Ford's limit on |f(x)|, one iteration earlier than "
        "Ford reports; on Ford's platform, a slightly different rounding of that function value keeps it above the "
        "limit",
    ),
    "5[0.03,0.09]": (
        1,
        "the interval drops below Ford's width limit one iteration earlier than Ford reports; the steps near the root "
        "depend on the last bits of the function values, which differ between Ford's platform and the platform that "
        "runs this test",
    ),
    "5[0.025,0.5]": (1, F_EQUALS_ZERO_DEVIATION_REASON),
}

FORD_TABLE_4 = ford_table_4_problems(_FORD_TABLE_4_ROWS, _FORD_TABLE_4_DEVIATIONS)
