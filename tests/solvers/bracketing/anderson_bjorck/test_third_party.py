"""These tests assert that `AndersonBjorck` reproduces third parties' published results for it."""

import pytest

from sunnbear.solvers import AndersonBjorck
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import FordTable4Problem, assert_n_fevals_at_ford_stop_reproduced

from .third_party_problems import FORD_TABLE_4


def test_the_rows_of_table_4_of_ford_name_every_problem_of_the_table_in_order():
    """`FORD_TABLE_4` holds 1 problem per member of `FordTable4Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in FORD_TABLE_4] == [member.value.name for member in FordTable4Problem]


@pytest.mark.parametrize("problem", FORD_TABLE_4, ids=str)
def test_the_iteration_counts_of_table_4_of_ford_are_reproduced(problem: PaperProblem):
    """On every row of Table 4 of Ford (1997), `AndersonBjorck` takes Ford's count of iterations until Ford's
    stopping rule stops it."""
    # --- act / assert -----------------
    assert_n_fevals_at_ford_stop_reproduced(AndersonBjorck(), problem)
