"""These tests assert that `Brent` reproduces the evaluation counts of Table 4.1 of Brent's 1973 book, on the rows
whose functions do not underflow near the root."""

import pytest

from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import Brent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import TABLE_4_1_WITH_T


@pytest.mark.parametrize("problem, t", TABLE_4_1_WITH_T, ids=str)
def test_the_evaluation_counts_of_table_4_1_of_the_book_are_reproduced(problem: PaperProblem, t: float):
    """On the rows of Table 4.1 whose functions do not underflow near the root, the number of function evaluations of
    `Brent` with the book's tolerance ``t`` is within the row's allowed deviation of the book's count."""
    # --- arrange ----------------------
    # `Brent` derives ``t`` from ``xtol`` (see its class docstring); the line below inverts that formula, so that
    # `Brent` runs with the book's ``t``.
    xtol = 2.0 * t + 6.0 * FLOAT64_EPS * max(abs(problem.a), abs(problem.b))

    # --- act --------------------------
    result = Brent().solve(problem.f, problem.a, problem.b, xtol=xtol, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
