"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`AndersonBjorck`."""

from dataclasses import replace

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import FORD_TABLE_4_PROBLEMS

# The rows of Ford's Table 4, with Ford's iteration counts for `AndersonBjorck`; a row that Ford prints as "200+"
# (more than 200 iterations) holds 200 as a lower bound.
_FORD_TABLE_4_ROWS = [
    {"name": "1[0.5,2]", "n_iterations": 5},
    {"name": "1[0.2,6]", "n_iterations": 5},
    {"name": "1[0.004,200]", "n_iterations": 7},
    {"name": "2[0.9,1.1]", "n_iterations": 7},
    {"name": "2[0.5,1.5]", "n_iterations": 12},
    {"name": "2[-5,10]", "n_iterations": 45},
    {"name": "3[550,560]", "n_iterations": 5},
    {"name": "3[400,600]", "n_iterations": 18},
    {"name": "3[350,850]", "n_iterations_lower_bound": 200},
    {"name": "4[0,1]", "n_iterations": 11},
    {"name": "4[-0.1,1.5]", "n_iterations": 43},
    {"name": "4[-0.5,2]", "n_iterations_lower_bound": 200},
    {"name": "5[0.035,0.05]", "n_iterations": 18},
    {"name": "5[0.03,0.09]", "n_iterations_lower_bound": 200},
    {"name": "5[0.025,0.5]", "n_iterations_lower_bound": 200},
]


def _ford_table_4_problem(row: dict) -> PaperProblem:
    """Return the problem that ``row`` names, with Ford's count or lower bound in sunnbear's counting, which adds the 2
    evaluations at the interval bounds to Ford's iterations."""
    if "n_iterations_lower_bound" in row:
        return replace(FORD_TABLE_4_PROBLEMS[row["name"]], n_fevals_lower_bound=row["n_iterations_lower_bound"] + 2)
    else:
        return replace(FORD_TABLE_4_PROBLEMS[row["name"]], n_fevals=row["n_iterations"] + 2)


FORD_TABLE_4 = [_ford_table_4_problem(row) for row in _FORD_TABLE_4_ROWS]
