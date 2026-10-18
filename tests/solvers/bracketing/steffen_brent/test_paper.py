"""These tests assert that `SteffenBrent` reproduces the published results of its paper, as this package's docstring
lists them."""

import pytest

from sunnbear.solvers import SteffenBrent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import CASE_STUDIES, FIGURE_VALUES

# The paper prints a tolerance of 1e-10 for its second case study, and none for the first.
_XTOL = 1e-10


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_case_studies_of_the_paper_are_reproduced(problem: PaperProblem):
    """`SteffenBrent` returns the paper's root on each of its case studies, and evaluates as often as the paper's runs
    do, to within the problem's ``n_fevals_tol``."""
    # --- act --------------------------
    result = _SteffenBrentWithPapersSecantStep().solve(problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_values_in_the_papers_figures_are_reproduced(problem: PaperProblem):
    """On each case study, the solve's first iterations, as many as the figures plot, match the figures' ``|f(b_k)|``
    and width ratios to the precision of reading the plots."""
    # --- act --------------------------
    result = _SteffenBrentWithPapersSecantStep().solve(
        problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    FIGURE_VALUES[problem.name].assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _SteffenBrentWithPapersSecantStep(SteffenBrent):
    """`_SteffenBrentWithPapersSecantStep` is `SteffenBrent` with its secant step in the form of the paper's equation
    4, a step from ``b``."""

    @staticmethod
    def _secant_zero(a: float, fa: float, b: float, fb: float) -> float:
        """Return ``a - fa * (b - a) / (fb - fa)``, as equation 4 computes the step from ``a``, the solve's ``b``."""
        return a - fa * (b - a) / (fb - fa)
