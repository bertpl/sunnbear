"""This module holds `FORD_TABLE_4`, the problems of Table 4 of Ford (1997), each with Ford's iteration count for
`Pegasus`."""

from dataclasses import replace

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import FORD_TABLE_4_PROBLEMS

# The rows of Ford's Table 4, with Ford's iteration counts for `Pegasus`.
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

_EXACT_ZERO_DEVIATION_REASON = (
    "the solve evaluates f(x) == 0 one iteration before Ford's stop; near the root, the function value consists of "
    "rounding error, which differs between Ford's platform and the platform that runs this test"
)
# `_FORD_TABLE_4_DEVIATIONS` maps the name of each row whose count `Pegasus` does not reproduce exactly to the
# allowed deviation and its reason.
_FORD_TABLE_4_DEVIATIONS = {
    "4[0,1]": (1, _EXACT_ZERO_DEVIATION_REASON),
    "5[0.035,0.05]": (1, _EXACT_ZERO_DEVIATION_REASON),
    "5[0.03,0.09]": (1, _EXACT_ZERO_DEVIATION_REASON),
}


def _ford_table_4_problem(row: dict) -> PaperProblem:
    """Return the problem that ``row`` names, with Ford's count in sunnbear's counting, which adds the 2 evaluations
    at the interval bounds to Ford's iterations, and the allowed deviation from that count, if any."""
    n_fevals_tol, deviation_reason = _FORD_TABLE_4_DEVIATIONS.get(row["name"], (0, None))
    return replace(
        FORD_TABLE_4_PROBLEMS[row["name"]],
        n_fevals=row["n_iterations"] + 2,
        n_fevals_tol=n_fevals_tol,
        deviation_reason=deviation_reason,
    )


FORD_TABLE_4 = [_ford_table_4_problem(row) for row in _FORD_TABLE_4_ROWS]
