import pytest

from sunnbear.solvers import RegulaFalsi, SolveStatus


def test_converges_on_gentle_function():
    # --- act --------------------------
    result = RegulaFalsi().solve(lambda x: x - 0.37, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == pytest.approx(0.37, abs=1e-9)


def test_stalls_on_high_curvature_and_hits_budget():
    """The retained-endpoint pathology: the bracket never contracts to xtol, so the budget terminates the run."""
    # --- arrange ----------------------
    def septic(x: float) -> float:
        return x**7 - 0.5

    # --- act --------------------------
    result = RegulaFalsi().solve(septic, -2.0, 2.0, xtol=1e-9, max_fevals=50)

    # --- assert -----------------------
    assert result.status == SolveStatus.MAX_FEVALS
    assert result.n_fevals == 50
    assert -2.0 < result.x < 2.0  # best-so-far estimate, not garbage


def test_sign_normalization():
    # --- act --------------------------
    result = RegulaFalsi().solve(lambda x: 0.25 - x, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == pytest.approx(0.25, abs=1e-9)


def test_uses_fewer_fevals_than_bisection_on_near_linear_function():
    # --- arrange ----------------------
    from sunnbear.solvers import Bisection

    def near_linear(x: float) -> float:
        return x - 0.123456789

    # --- act --------------------------
    result_rf = RegulaFalsi().solve(near_linear, 0.0, 1.0, xtol=1e-12, max_fevals=100)
    result_bi = Bisection().solve(near_linear, 0.0, 1.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert result_rf.status == SolveStatus.CONVERGED
    assert result_rf.n_fevals < result_bi.n_fevals
