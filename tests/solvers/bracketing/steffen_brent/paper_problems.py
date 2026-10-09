"""This module holds `CASE_STUDIES`, the 2 case studies of the Steffen-Brent paper, with the roots that the paper
reports for them."""

import math

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
        "case_study_1",
        _case_study_1,
        1.0,
        3.0,
        root=2.1584212093,
        root_abs_tol=5e-11,
        # The paper reports 6 iterations. `SteffenBrent` evaluates at the 2 interval bounds, once in each of those 6
        # iterations, and 3 more times at the midpoint.
        n_fevals=2 + 6 + 3,
    ),
    # The tolerance on the root covers the gap between the paper's root and the root at the full-precision
    # Peng-Robinson constants, which the comment on those constants gives.
    PaperProblem("case_study_2", _case_study_2, 14.0, 17.0, root=15.0676609061, root_abs_tol=1e-8),
]
