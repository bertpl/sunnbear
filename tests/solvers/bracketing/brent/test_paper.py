"""These tests assert that `Brent` reproduces the evaluation counts of Table 4.1 of Brent's 1973 book, where its
procedure ``zero`` applies."""

import pytest

from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import Brent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import TABLE_4_1


@pytest.mark.parametrize("problem, t", TABLE_4_1, ids=str)
def test_the_evaluation_counts_of_table_4_1_of_the_book_are_reproduced(problem: PaperProblem, t: float):
    """On the rows of Table 4.1 that need no extended exponent range, `Brent` with the book's tolerance ``t``
    evaluates within a few evaluations as often as the book reports.

    `Brent` derives ``t`` from ``xtol`` as ``t = (xtol - 6 * macheps * max(|a|, |b|)) / 2``, so the test passes the
    ``xtol`` that gives the book's ``t``.
    """
    # --- arrange ----------------------
    xtol = 2.0 * t + 6.0 * FLOAT64_EPS * max(abs(problem.a), abs(problem.b))

    # --- act --------------------------
    result = Brent().solve(problem.f, problem.a, problem.b, xtol=xtol, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
