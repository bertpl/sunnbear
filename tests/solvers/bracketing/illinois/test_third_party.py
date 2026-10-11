"""These tests assert that `Illinois` reproduces the results that third parties publish for it."""

import pytest

from sunnbear.solvers import Illinois
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import n_fevals_at_ford_stop

from .third_party_problems import FORD_TABLE_4

# The evaluation budget of the solves; it exceeds every count that Ford prints, "200+" included.
_MAX_FEVALS = 300


@pytest.mark.parametrize("problem", FORD_TABLE_4, ids=str)
def test_the_iteration_counts_of_table_4_of_ford_are_reproduced(problem: PaperProblem):
    """On every row of Table 4 of Ford (1997), `Illinois` takes Ford's count of iterations until Ford's stopping rule
    stops it, within the row's allowed deviation.

    `Illinois` solves with ``xtol = 0``, so that its own stopping rule stops it only on ``f(x) == 0``, where
    Ford's rule stops too; the test then finds Ford's stop in the solve's history.
    """
    # --- act --------------------------
    result = Illinois().solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=_MAX_FEVALS, history_enabled=True)

    # --- assert -----------------------
    problem.assert_n_fevals_reproduced(n_fevals_at_ford_stop(result), max_fevals=_MAX_FEVALS)
