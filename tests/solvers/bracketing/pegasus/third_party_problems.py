"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`Pegasus`."""

from tests.solvers.paper_problems.ford import F_EQUALS_ZERO_DEVIATION_REASON, ford_table_4_problems

# `_FORD_TABLE_4_ROWS` holds the rows of Ford's Table 4, with Ford's iteration counts for `Pegasus`.
_FORD_TABLE_4_ROWS = [
    {"name": "1[0.5,2]", "n_iterations": 6},
    {"name": "1[0.2,6]", "n_iterations": 10},
    {"name": "1[0.004,200]", "n_iterations": 18},
    {"name": "2[0.9,1.1]", "n_iterations": 7},
    {"name": "2[0.5,1.5]", "n_iterations": 14},
    {"name": "2[-5,10]", "n_iterations": 103},
    {"name": "3[550,560]", "n_iterations": 5},
    {"name": "3[400,600]", "n_iterations": 27},
    {"name": "3[350,850]", "n_iterations": 42},
    {"name": "4[0,1]", "n_iterations": 10},
    {"name": "4[-0.1,1.5]", "n_iterations": 14},
    {"name": "4[-0.5,2]", "n_iterations": 31},
    {"name": "5[0.035,0.05]", "n_iterations": 14},
    {"name": "5[0.03,0.09]", "n_iterations": 26},
    {"name": "5[0.025,0.5]", "n_iterations": 46},
]

# `_FORD_TABLE_4_DEVIATIONS` maps the name of each row whose count `Pegasus` does not reproduce exactly to the
# allowed deviation and its reason.
_FORD_TABLE_4_DEVIATIONS = {
    "4[0,1]": (1, F_EQUALS_ZERO_DEVIATION_REASON),
    "5[0.035,0.05]": (1, F_EQUALS_ZERO_DEVIATION_REASON),
    "5[0.03,0.09]": (1, F_EQUALS_ZERO_DEVIATION_REASON),
}

FORD_TABLE_4 = ford_table_4_problems(_FORD_TABLE_4_ROWS, _FORD_TABLE_4_DEVIATIONS)
