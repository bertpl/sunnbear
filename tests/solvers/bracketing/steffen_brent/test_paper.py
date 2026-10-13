"""These tests assert that `SteffenBrent` reproduces the published results of its paper: the roots and iteration counts
of its 2 case studies, and the iterates of the modified method that its figures plot."""

import math

import pytest

from sunnbear.solvers import SolveResult, SteffenBrent
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import CASE_STUDIES, FIGURE_ITERATES

# The paper prints a tolerance of 1e-10 for its second case study, and none for the first.
_XTOL = 1e-10

# Below this |f|, the figures' values lie at the level of rounding in f.
_ROUNDING_LEVEL_ABS_F = 1e-12


def _iterates(result: SolveResult) -> tuple[list[float], list[float]]:
    """Return ``|f(b_k)|`` for each ``k`` from 0, and the width ratio of each iteration, of a solve's history.

    The interval after each iteration follows from the evaluations by the rule that the `SteffenBrent` class
    docstring states: each iteration evaluates ``s``, and also the midpoint of ``a`` and ``s`` when ``f(a)`` and
    ``f(s)`` differ in sign and ``f(s)`` is not 0.
    """
    (a, fa), (b, fb), *evaluations = result.history
    if abs(fa) < abs(fb):
        a, b, fa, fb = b, a, fb, fa
    abs_fb, width_ratios = [abs(fb)], []
    while evaluations:
        width = abs(b - a)
        s, fs = evaluations.pop(0)
        if (fa > 0.0) == (fs > 0.0):
            a, fa = b, fb
        elif fs != 0.0:
            m, fm = evaluations.pop(0)
            assert m == (a + s) / 2.0
            if (fm > 0.0 > fs) or (fm < 0.0 < fs):
                a, fa = m, fm
        b, fb = s, fs
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
        abs_fb.append(abs(fb))
        width_ratios.append(abs(b - a) / width)
    return abs_fb, width_ratios


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_case_studies_of_the_paper_are_reproduced(problem: PaperProblem):
    """`SteffenBrent` returns the paper's root on each of its case studies, and evaluates as often as the paper's runs
    do, up to the deviation that the problem states."""
    # --- act --------------------------
    result = SteffenBrent().solve(problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem", CASE_STUDIES, ids=str)
def test_the_iterates_of_the_papers_figures_are_reproduced(problem: PaperProblem):
    """On each case study, the first 6 iterations reproduce the figures' ``|f(b_k)|`` within 0.1 decades, and their
    width ratios within 0.02, the precision of reading the plots; an ``|f(b_k)|`` at the level of rounding in ``f``
    only has to lie at that level too."""
    # --- arrange ----------------------
    figure = FIGURE_ITERATES[problem.name]

    # --- act --------------------------
    result = SteffenBrent().solve(problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100, history_enabled=True)
    abs_fb, width_ratios = _iterates(result)

    # --- assert -----------------------
    for abs_fb_solve, abs_fb_figure in zip(abs_fb[: len(figure.abs_fb)], figure.abs_fb, strict=True):
        if abs_fb_figure < _ROUNDING_LEVEL_ABS_F:
            assert abs_fb_solve < _ROUNDING_LEVEL_ABS_F
        else:
            assert math.log10(abs_fb_solve) == pytest.approx(math.log10(abs_fb_figure), abs=0.1)
    assert width_ratios[: len(figure.width_ratios)] == pytest.approx(figure.width_ratios, abs=0.02)
