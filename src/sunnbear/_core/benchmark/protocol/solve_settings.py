"""`compute_solve_settings` maps tuples onto the `xtol` and `c` values and the budget of a test problem's solves."""

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.problems.core import TestProblem

from .tolerances import compute_xtol_range, max_fevals_for


def compute_solve_settings(
    problem: TestProblem, *, mc_tuples: MCTuples, n_bisection_fevals: int
) -> tuple[np.ndarray, np.ndarray, int]:
    """Return the `xtol` array and the `c` array of every tuple of `mc_tuples` for `problem`, and the evaluation budget.

    `xtol` lies within the range from `compute_xtol_range`, `c` within the c-range of `problem`, and the budget is
    `max_fevals_for(n_bisection_fevals=n_bisection_fevals)`.
    """
    xtol_min, xtol_max = compute_xtol_range(a=problem.a, b=problem.b, n_bisection_fevals=n_bisection_fevals)
    xtols, cs = mc_tuples.to_xtol_and_c(xtol_min=xtol_min, xtol_max=xtol_max, c_min=problem.c_min, c_max=problem.c_max)
    return xtols, cs, max_fevals_for(n_bisection_fevals=n_bisection_fevals)
