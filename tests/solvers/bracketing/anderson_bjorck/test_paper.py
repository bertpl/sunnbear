"""These tests assert that `AndersonBjorck` reproduces the iteration counts of Examples 1 to 7 of its paper."""

import pytest

from sunnbear.solvers import AndersonBjorck
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.anderson_bjorck import AndersonBjorckExampleProblem

from .paper_problems import EXAMPLES_1_TO_7

# The paper ran Examples 1 to 7 with its tolerance ``delta`` at 6e-8; `AndersonBjorck` sets ``delta = xtol``.
_PAPER_DELTA = 6e-8


def test_the_rows_of_examples_1_to_7_name_every_problem_of_the_examples_in_order():
    """`EXAMPLES_1_TO_7` holds 1 problem per member of `AndersonBjorckExampleProblem`, in the paper's order."""
    # --- assert -----------------------
    assert [problem.name for problem in EXAMPLES_1_TO_7] == [
        member.value.name for member in AndersonBjorckExampleProblem
    ]


@pytest.mark.parametrize("problem", EXAMPLES_1_TO_7, ids=str)
def test_the_iteration_counts_of_examples_1_to_7_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every run of Examples 1 to 7 of Anderson and Björck (1973), `AndersonBjorck` takes the paper's count of
    iterations, within the row's allowed deviation, with its steps of delta at the paper's ``delta``.

    The paper's runs stop once the interval is narrower than ``delta``; `AndersonBjorck` stops by the shared stopping
    criterion, once the interval is at most ``2*delta`` wide.

    The test does not apply the paper's stopping criterion: in float64, 10 of the 26 runs then alternate between 2
    x-values whose computed distance exceeds ``delta`` by a rounding error, and never end, while the other 16 take the
    same counts as under the shared stopping criterion.
    """
    # --- act --------------------------
    result = AndersonBjorck().solve(problem.f, problem.a, problem.b, xtol=_PAPER_DELTA, max_fevals=50)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
