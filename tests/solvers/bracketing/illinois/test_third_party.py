"""These tests assert that `Illinois` reproduces third parties' published results for it."""

import pytest

from sunnbear.solvers import Illinois
from tests.solvers.paper_problems import PaperProblem, PaperProblemEnum
from tests.solvers.paper_problems.ford import FordTable4Problem, assert_n_fevals_at_ford_stop_reproduced
from tests.solvers.paper_problems.oliveira_takahashi import OLIVEIRA_TAKAHASHI_XTOL, OliveiraTakahashiTable1Problem

from .third_party_problems import FORD_TABLE_4, OLIVEIRA_TAKAHASHI_TABLE_1


@pytest.mark.parametrize(
    "table, problem_enum",
    [(FORD_TABLE_4, FordTable4Problem), (OLIVEIRA_TAKAHASHI_TABLE_1, OliveiraTakahashiTable1Problem)],
    ids=["ford_table_4", "oliveira_takahashi_table_1"],
)
def test_the_rows_of_each_table_name_every_problem_of_the_table_in_order(
    table: list[PaperProblem], problem_enum: type[PaperProblemEnum]
):
    """Each table holds 1 problem per member of its problem enum, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in table] == [member.value.name for member in problem_enum]


@pytest.mark.parametrize("problem", FORD_TABLE_4, ids=str)
def test_the_iteration_counts_of_table_4_of_ford_are_reproduced(problem: PaperProblem):
    """On every row of Table 4 of Ford (1997), `Illinois` takes Ford's count of iterations until Ford's stopping rule
    stops it, within the row's allowed deviation."""
    # --- act / assert -----------------
    assert_n_fevals_at_ford_stop_reproduced(Illinois(), problem)


@pytest.mark.parametrize("problem", OLIVEIRA_TAKAHASHI_TABLE_1, ids=str)
def test_the_iteration_counts_of_table_1_of_oliveira_takahashi_are_reproduced(problem: PaperProblem):
    """On every row of Table 1 of Oliveira and Takahashi (2020), `Illinois` takes the number of iterations in the
    column "Illinois", within the row's allowed deviation; the table's runs stop by the criterion of `Illinois`."""
    # --- act --------------------------
    result = Illinois().solve(problem.f, problem.a, problem.b, xtol=OLIVEIRA_TAKAHASHI_XTOL, max_fevals=200)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
