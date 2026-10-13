"""This module holds the published results of the Steffen-Brent paper: `CASE_STUDIES`, its 2 case studies with their
roots and iteration counts, and `FIGURE_VALUES`, the modified method's values in its figures."""

import math
from dataclasses import dataclass

import pytest

from sunnbear.solvers import SolveResult
from tests.solvers.paper_problems import PaperProblem


def _case_study_1(x: float) -> float:
    """Return the function of the paper's first case study, its equation 6."""
    return math.exp(-(x**2) / 4.0) - 2.0 * math.cos(x) + x / 2.0 - 2.5


# The Peng-Robinson constants, at full precision (Peng and Robinson, 1976): the paper prints them rounded to
# Λ = 0.45724 and Γ = 0.07780, but the paper's root lies within 6.5e-9 of the root at the full-precision constants, and
# not near the root at the rounded ones.
_PENG_ROBINSON_ETA = 1.0 / (1.0 + (4.0 - math.sqrt(8.0)) ** (1.0 / 3.0) + (4.0 + math.sqrt(8.0)) ** (1.0 / 3.0))
_PENG_ROBINSON_CAPITAL_LAMBDA = (8.0 + 40.0 * _PENG_ROBINSON_ETA) / (49.0 - 37.0 * _PENG_ROBINSON_ETA)
_PENG_ROBINSON_CAPITAL_GAMMA = _PENG_ROBINSON_ETA / (3.0 + _PENG_ROBINSON_ETA)


def _case_study_2(v: float) -> float:
    """Return the function of the paper's second case study: its equation 8 with the Peng-Robinson parameters of its
    equation 9, at ``omega = 0.2``, ``Tr = 0.85`` and ``Pr = 0.45``, where ``v`` is the volume ``V`` divided by the
    co-volume parameter ``b``."""
    lam, sigma, omega, tr, pr = 2.0, -1.0, 0.2, 0.85, 0.45
    alpha = (1.0 + (0.37464 + 1.54226 * omega - 0.26992 * omega**2) * (1.0 - math.sqrt(tr))) ** 2
    t = tr / (_PENG_ROBINSON_CAPITAL_GAMMA * pr)
    u = _PENG_ROBINSON_CAPITAL_LAMBDA * alpha / (_PENG_ROBINSON_CAPITAL_GAMMA**2 * pr)
    return v**3 - (1.0 - lam + t) * v**2 + (sigma - lam - lam * t + u) * v - (sigma + sigma * t + u)


CASE_STUDIES = [
    PaperProblem(
        name="case_study_1",
        f=_case_study_1,
        a=1.0,
        b=3.0,
        # The paper prints the root to 4 decimals.
        root=2.1584,
        root_abs_tol=5e-5,
        # The paper's figures show 6 iterations. The run evaluates:
        # - at the 2 interval bounds;
        # - once in each iteration;
        # - in 2 of those iterations, also at the midpoint of ``a`` and ``s``.
        n_fevals=2 + 6 + 2,
        n_fevals_tol=1,
        deviation_reason=(
            "The paper's run stops once |f(b)| is small enough, with |f(b)| about 1e-15 after 6 iterations; "
            "`SteffenBrent` stops on the width of the interval, and takes a 7th iteration, which ends at an exact zero."
        ),
    ),
    PaperProblem(
        name="case_study_2",
        f=_case_study_2,
        a=14.0,
        b=17.0,
        # The tolerance on the root covers the gap between the paper's root and the root at the full-precision
        # Peng-Robinson constants; the comment above `_PENG_ROBINSON_ETA` gives that gap.
        root=15.0676609061,
        root_abs_tol=1e-8,
        # The paper's figures show 6 iterations; the evaluations are counted as in the first case study.
        n_fevals=2 + 6 + 2,
    ),
]


@dataclass(frozen=True)
class FigureValues:
    """A `FigureValues` holds the values of the modified method in 1 case study, as read from the paper's figures.

    Attributes:
        abs_fb: ``|f(b_k)|`` for each ``k`` from 0, read from the log-scale plot of Figure 3(b) or 6(b).
        width_ratios: For each iteration, the width of the new interval divided by that of the old one, read from the
            linear-scale plot of Figure 4(b) or 7(b). The paper calls it the relative interval reduction without
            defining it; the width ratio is the measure that reproduces the panels for Dekker's method in the same
            figures.
    """

    abs_fb: tuple[float, ...]
    width_ratios: tuple[float, ...]

    # A figure's |f| below this value lies at the level of rounding in f, so the solve's |f| only has to lie below it
    # too.
    _ROUNDING_LEVEL_ABS_F = 1e-12

    def assert_reproduced_by(self, result: SolveResult) -> None:
        """Assert that the iterations that the figures plot reproduce the figures' values to the precision of reading
        the plots; an ``|f(b_k)|`` at the level of rounding in ``f`` only has to lie at that level too.

        ``result`` must hold the solve's history.
        """
        abs_fb, width_ratios = self._compute_values(result)
        for abs_fb_solve, abs_fb_figure in zip(abs_fb[: len(self.abs_fb)], self.abs_fb, strict=True):
            if abs_fb_figure < self._ROUNDING_LEVEL_ABS_F:
                assert abs_fb_solve < self._ROUNDING_LEVEL_ABS_F
            else:
                assert math.log10(abs_fb_solve) == pytest.approx(math.log10(abs_fb_figure), abs=0.1)
        assert width_ratios[: len(self.width_ratios)] == pytest.approx(self.width_ratios, abs=0.02)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _compute_values(result: SolveResult) -> tuple[list[float], list[float]]:
        """From a solve's history, return ``|f(b_k)|`` for each ``k`` from 0, and for each iteration the width of the
        new interval divided by that of the old one.

        The interval after each iteration follows from the evaluations by the rule in the `SteffenBrent` class
        docstring: each iteration evaluates ``s``, and also the midpoint of ``a`` and ``s`` when ``f(a)`` and ``f(s)``
        differ in sign and ``f(s)`` is not 0.
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


FIGURE_VALUES = {
    "case_study_1": FigureValues(
        abs_fb=(1.1, 0.35, 0.065, 3.8e-3, 3.2e-5, 3.2e-10, 1.3e-15),
        width_ratios=(0.34, 0.35, 0.16, 0.47, 0.0, 0.0),
    ),
    "case_study_2": FigureValues(
        abs_fb=(95.0, 37.0, 2.5, 0.17, 7.5e-4, 8e-10, 4e-13),
        width_ratios=(0.38, 0.32, 0.065, 0.47, 0.0, 0.0),
    ),
}
