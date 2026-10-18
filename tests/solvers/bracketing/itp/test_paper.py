"""These tests assert that `ITP` reproduces the iteration counts of Table 1 of its paper."""

import pytest

from sunnbear.solvers import ITP, ITPVariant
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.oliveira_takahashi import OLIVEIRA_TAKAHASHI_XTOL, OliveiraTakahashiTable1Problem
from tests.solvers.paper_problems.secant_forms import with_textbook_secant_zero

from .paper_problems import TABLE_1


def test_the_rows_of_table_1_name_every_problem_of_the_table_in_order():
    """`TABLE_1` holds 1 problem per member of `OliveiraTakahashiTable1Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_1] == [member.value.name for member in OliveiraTakahashiTable1Problem]


@pytest.mark.parametrize("problem", TABLE_1, ids=str)
def test_the_iteration_counts_of_table_1_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every function of the paper's Table 1, the paper_experiments variant with ``n_slack = 0`` takes as many
    iterations as the paper reports, except on the step function, where its count may differ by 1.

    The paper's table comes from the authors' MATLAB code, which the paper_experiments variant follows, and which
    computes ``x_f`` in the textbook form of the secant's zero.
    """
    # --- act --------------------------
    result = with_textbook_secant_zero(ITP)(n_slack=0, variant=ITPVariant.PAPER_EXPERIMENTS).solve(
        problem.f, problem.a, problem.b, xtol=OLIVEIRA_TAKAHASHI_XTOL, max_fevals=100
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
