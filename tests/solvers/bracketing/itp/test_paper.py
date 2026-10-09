"""These tests assert that `ITP` reproduces the iteration counts of Table 1 of its paper."""

import pytest

from sunnbear.solvers import ITP, ITPVariant
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import TABLE_1, XTOL


@pytest.mark.parametrize("problem", TABLE_1, ids=str)
def test_the_iteration_counts_of_table_1_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every function of the paper's Table 1, the paper_experiments variant with ``n_slack = 0`` takes as many
    iterations as the paper reports, except on the step function, where its count may differ by 1.

    The paper's table comes from the authors' MATLAB code, which the paper_experiments variant follows.
    """
    # --- act --------------------------
    result = ITP(n_slack=0, variant=ITPVariant.PAPER_EXPERIMENTS).solve(
        problem.f, problem.a, problem.b, xtol=XTOL, max_fevals=100
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
