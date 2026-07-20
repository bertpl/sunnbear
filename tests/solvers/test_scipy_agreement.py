"""Cross-checks of our solver implementations against SciPy ground truth.

SciPy is a dev-dependency for exactly this purpose; the shipped package does
not depend on it. Agreement is asserted on the found root (both solvers land
within tolerance of the same root), not on evaluation counts — the stopping
criteria differ in detail.
"""

import pytest
import scipy.optimize

from sunnbear.solvers import Bisection, RegulaFalsi, SolveStatus

XTOL = 1e-10


def _test_functions():
    return [
        (lambda x: x - 0.37, 0.0, 1.0),
        (lambda x: x**3 - 0.5 * x - 0.2, -2.0, 2.0),
        (lambda x: 0.25 - x, 0.0, 1.0),  # decreasing: exercises sign normalization
    ]


@pytest.mark.parametrize("f, a, b", _test_functions())
def test_bisection_agrees_with_scipy_bisect(f, a, b):
    # --- act --------------------------
    ours = Bisection().solve(f, a, b, xtol=XTOL, max_fevals=200)
    scipy_x = scipy.optimize.bisect(f, a, b, xtol=XTOL / 10)

    # --- assert -----------------------
    assert ours.status == SolveStatus.CONVERGED
    assert ours.x == pytest.approx(scipy_x, abs=2 * XTOL)


@pytest.mark.parametrize(
    "f, a, b",
    [
        # near-linear only: on curved functions pure regula falsi retains one endpoint, so its
        # bracket never contracts to the width-based stopping criterion (the documented stall)
        (lambda x: x - 0.37, 0.0, 1.0),
        (lambda x: 0.25 - x, 0.0, 1.0),
    ],
)
def test_regula_falsi_agrees_with_scipy_root(f, a, b):
    # --- act --------------------------
    ours = RegulaFalsi().solve(f, a, b, xtol=XTOL, max_fevals=200)
    scipy_x = scipy.optimize.brentq(f, a, b, xtol=XTOL / 10)

    # --- assert -----------------------
    assert ours.status == SolveStatus.CONVERGED
    assert ours.x == pytest.approx(scipy_x, abs=2 * XTOL)
