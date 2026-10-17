"""These tests assert that `SteffenBrent`, with the stopping criterion of its paper's Algorithm 2, reproduces the
published results of its paper, as this package's docstring lists them."""

import pytest

from sunnbear.solvers import SteffenBrent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import CASE_STUDIES, FIGURE_VALUES

# The paper prints 1 tolerance, 1e-10, for its second case study, and none for the first.
_XTOL = 1e-10


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_case_studies_of_the_paper_are_reproduced(problem: PaperProblem):
    """`SteffenBrent` with Algorithm 2's stopping criterion returns the paper's root on each of its case studies, and
    evaluates as often as the paper's runs do, to within the problem's ``n_fevals_tol``."""
    # --- act --------------------------
    result = _SteffenBrentWithPaperStoppingCriterion().solve(
        problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_values_in_the_papers_figures_are_reproduced(problem: PaperProblem):
    """On each case study, the iterations of `SteffenBrent` with Algorithm 2's stopping criterion, as many as the
    figures plot, match the figures' ``|f(b_k)|`` and width ratios to the precision of reading the plots."""
    # --- act --------------------------
    result = _SteffenBrentWithPaperStoppingCriterion().solve(
        problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    FIGURE_VALUES[problem.name].assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _SteffenBrentWithPaperStoppingCriterion(SteffenBrent):
    """`_SteffenBrentWithPaperStoppingCriterion` is `SteffenBrent` with the stopping criterion and the return value of
    the paper's Algorithm 2: the solve ends once ``|b - a| <= tol1`` or ``|f(b)| <= tol2``, and returns ``b``.

    The paper prints 1 tolerance, so this class sets both ``tol1`` and ``tol2`` to ``xtol``, and a test passes the
    paper's tolerance as ``xtol``.
    """

    @staticmethod
    def _root_if_converged(a: float, fa: float, b: float, fb: float, xtol_doubled: float) -> float | None:
        """Return ``b`` once ``|b - a| <= tol1`` or ``|f(b)| <= tol2``, with ``tol1 = tol2 = xtol_doubled / 2``, or
        ``None`` if the solve continues."""
        tol = 0.5 * xtol_doubled
        if abs(b - a) <= tol or abs(fb) <= tol:
            return b
        else:
            return None
