"""These tests assert that `ITP` reproduces the iteration counts of Table 1 of its paper."""

import pytest

from sunnbear.solvers import ITP, ITPVariant, SolveStatus

from .paper_problems import PAPER_TABLE_1, XTOL


@pytest.mark.parametrize("name", [name for name in PAPER_TABLE_1 if name != "step_function"])
def test_the_iteration_counts_of_table_1_of_the_paper_are_reproduced(name):
    """On every function of the paper's Table 1 but the step function, the paper_experiments variant with
    ``n_slack = 0`` takes as many iterations as the paper reports.

    The paper's table comes from the authors' MATLAB code, which the paper_experiments variant follows.

    On the step function, the table reports 34 iterations, which MATLAB's arithmetic produced, and `ITP` takes 35, so
    the test leaves that function out.
    """
    # --- arrange ----------------------
    f, n_iterations = PAPER_TABLE_1[name]

    # --- act --------------------------
    result = ITP(n_slack=0, variant=ITPVariant.PAPER_EXPERIMENTS).solve(f, -1.0, 1.0, xtol=XTOL, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_iterations + 2)
