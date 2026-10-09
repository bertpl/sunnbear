"""These tests assert that `Chandrupatla` reproduces the evaluation counts of Table 2 of its paper."""

import pytest

from sunnbear.solvers import Chandrupatla
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import TABLE_2


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every row of the paper's Table 2, `Chandrupatla` evaluates exactly as often as the paper reports.

    The paper's absolute tolerance is 1e-5, and its relative tolerance of 1e-10 makes no difference to these counts,
    so the solver's ``xtol`` of 1e-5 reproduces them.
    """
    # --- act --------------------------
    result = Chandrupatla().solve(problem.f, problem.a, problem.b, xtol=1e-5, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
