"""These tests assert that `SteffenBrent` reproduces the 2 case studies of its paper."""

import math

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent


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


def test_case_study_1_reaches_the_papers_root_in_its_6_iterations():
    """On the paper's first case study over ``[1, 3]``, `SteffenBrent` returns the paper's root 2.1584212093.

    The 11 evaluations are:

    - 2 at the interval bounds;
    - 1 in each of the paper's 6 iterations;
    - 3 more at the midpoint.
    """
    # --- act --------------------------
    result = SteffenBrent().solve(_case_study_1, 1.0, 3.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(2.1584212093, abs=5e-11)
    assert result.n_fevals == 11


def test_case_study_2_reaches_the_papers_root():
    """On the paper's second case study over ``[14, 17]``, at the paper's tolerance of 1e-10, `SteffenBrent` returns a
    root within 1e-8 of the paper's root 15.0676609061.

    The tolerance covers the gap between the paper's root and the root at the full-precision constants, which the
    comment on those constants gives.
    """
    # --- act --------------------------
    result = SteffenBrent().solve(_case_study_2, 14.0, 17.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(15.0676609061, abs=1e-8)
