"""These tests assert that `Pegasus` reproduces third parties' published results for it."""

import pytest

from sunnbear.solvers import Pegasus
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ford import assert_n_fevals_at_ford_stop_reproduced

from .third_party_problems import FORD_TABLE_4


@pytest.mark.parametrize("problem", FORD_TABLE_4, ids=str)
def test_the_iteration_counts_of_table_4_of_ford_are_reproduced(problem: PaperProblem):
    """On every row of Table 4 of Ford (1997), `Pegasus` takes Ford's count of iterations until Ford's stopping rule
    stops it, within the row's allowed deviation."""
    # --- act / assert -----------------
    assert_n_fevals_at_ford_stop_reproduced(Pegasus(), problem)
