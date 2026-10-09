"""These tests assert that `SteffenBrent` reproduces the 2 case studies of its paper."""

import pytest

from sunnbear.solvers import SteffenBrent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import CASE_STUDIES


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_case_studies_of_the_paper_are_reproduced(problem: PaperProblem):
    """At the paper's tolerance of 1e-10, `SteffenBrent` returns the paper's root on each of its case studies, and on
    the first one evaluates as often as the paper's 6 iterations imply."""
    # --- act --------------------------
    result = SteffenBrent().solve(problem.f, problem.a, problem.b, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
