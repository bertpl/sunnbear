"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`AndersonBjorck`."""

from tests.solvers.paper_problems.ford import ford_table_4_problems

# `_FORD_TABLE_4_ROWS` holds the rows of Ford's Table 4, with Ford's iteration counts for `AndersonBjorck`; a row that
# Ford prints as "200+" (more than 200 iterations) holds 200 as a lower bound.
_FORD_TABLE_4_ROWS = [
    {"name": "1[0.5,2]", "n_iterations": 5},
    {"name": "1[0.2,6]", "n_iterations": 5},
    {"name": "1[0.004,200]", "n_iterations": 7},
    {"name": "2[0.9,1.1]", "n_iterations": 7},
    {"name": "2[0.5,1.5]", "n_iterations": 12},
    {"name": "2[-5,10]", "n_iterations": 45},
    {"name": "3[550,560]", "n_iterations": 5},
    {"name": "3[400,600]", "n_iterations": 18},
    {"name": "3[350,850]", "n_iterations_strict_lower_bound": 200},
    {"name": "4[0,1]", "n_iterations": 11},
    {"name": "4[-0.1,1.5]", "n_iterations": 43},
    {"name": "4[-0.5,2]", "n_iterations_strict_lower_bound": 200},
    {"name": "5[0.035,0.05]", "n_iterations": 18},
    {"name": "5[0.03,0.09]", "n_iterations_strict_lower_bound": 200},
    {"name": "5[0.025,0.5]", "n_iterations_strict_lower_bound": 200},
]

FORD_TABLE_4 = ford_table_4_problems(_FORD_TABLE_4_ROWS, {})
