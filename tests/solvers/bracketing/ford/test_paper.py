"""These tests assert that `Ford` reproduces the iteration counts of Methods 1, 3 and 4 in Table 4 of its paper."""

import pytest

from sunnbear.solvers import Ford, FordVariant
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import FordTable4Problem, assert_n_fevals_at_ford_stop_reproduced

from .paper_problems import TABLE_4_BY_VARIANT


@pytest.mark.parametrize("variant", FordVariant)
def test_the_rows_of_table_4_name_every_problem_of_the_table_in_order(variant: FordVariant):
    """For each variant, `TABLE_4_BY_VARIANT` holds 1 problem per member of `FordTable4Problem`, in the table's
    order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_4_BY_VARIANT[variant]] == [
        member.value.name for member in FordTable4Problem
    ]


@pytest.mark.parametrize(
    "variant, problem",
    [
        pytest.param(variant, problem, id=f"{variant}-{problem}")
        for variant, problems in TABLE_4_BY_VARIANT.items()
        for problem in problems
    ],
)
def test_the_iteration_counts_of_table_4_of_the_paper_are_reproduced(variant: FordVariant, problem: PaperProblem):
    """On every row of Table 4 of Ford (1997), each variant of `Ford` takes the paper's count of iterations for its
    method until the paper's stopping rule stops it, within the row's allowed deviation."""
    # --- act / assert -----------------
    assert_n_fevals_at_ford_stop_reproduced(Ford(variant=variant), problem)
