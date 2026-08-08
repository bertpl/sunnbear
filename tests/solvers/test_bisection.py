import math

import pytest

from sunnbear.solvers import Bisection, SolveStatus


def test_finds_root_within_xtol():
    # --- arrange ----------------------
    root = math.pi / 4

    # --- act --------------------------
    result = Bisection().solve(lambda x: x - root, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == pytest.approx(root, abs=1e-9)


@pytest.mark.parametrize("n_iters", [5, 10, 20])
def test_exact_iteration_count_within_xtol_band(n_iters):
    """Framework invariant: for xtol in ((b-a)*2^-(n+1), (b-a)*2^-n), bisection takes exactly n iterations."""
    # --- arrange ----------------------
    a, b = 0.0, 1.0
    xtol = 1.5 * 2.0 ** -(n_iters + 1)  # mid-band
    root = 1 / math.sqrt(2)  # no early exact hit

    # --- act --------------------------
    result = Bisection().solve(lambda x: x - root, a, b, xtol=xtol, max_fevals=1000)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.n_iters == n_iters
    assert result.n_fevals == n_iters + 2  # the two initial bracket evaluations
    assert result.x == pytest.approx(root, abs=xtol)


def test_sign_normalization_handles_decreasing_function():
    # --- act --------------------------
    result = Bisection().solve(lambda x: 0.5 - x, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == pytest.approx(0.5, abs=1e-9)


@pytest.mark.parametrize("root_at", [0.0, 1.0])
def test_exact_zero_at_endpoint_converges_immediately(root_at):
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - root_at, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == root_at
    assert result.n_fevals == 2


def test_exact_zero_mid_run_returns_endpoint():
    # --- act --------------------------
    # root at 0.5 is hit exactly by the first midpoint evaluation
    result = Bisection().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == 0.5
    assert result.n_fevals == 3


def test_same_sign_bracket_raises():
    with pytest.raises(ValueError):
        Bisection().solve(lambda x: x + 10.0, 0.0, 1.0, xtol=1e-9, max_fevals=100)


def test_flop_counts_cover_solver_but_not_function_body():
    # --- arrange ----------------------
    def cheap(x: float) -> float:
        return x - 0.7

    def expensive(x: float) -> float:
        return math.sin(math.exp(x) - math.e**0.7) + math.tan(x - 0.7) * math.cos(x * 0.0)

    # --- act --------------------------
    result_cheap = Bisection().solve(cheap, 0.0, 1.0, xtol=1e-6, max_fevals=100)
    result_expensive = Bisection().solve(expensive, 0.0, 1.0, xtol=1e-6, max_fevals=100)

    # --- assert -----------------------
    assert result_cheap.flop_counts.total_count() > 0
    # function-body cost is excluded, so algorithm flops match for equal iteration counts
    assert result_cheap.n_iters == result_expensive.n_iters
    assert result_cheap.flop_counts.as_dict() == result_expensive.flop_counts.as_dict()


def test_history_recording():
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.3, 0.0, 1.0, xtol=1e-2, max_fevals=100, record_history=True)

    # --- assert -----------------------
    assert result.history is not None
    assert len(result.history) == result.n_fevals
    assert result.history[0] == (0.0, -0.3)
    assert result.history[1] == (1.0, 0.7)


def test_solve_input_validation():
    # --- arrange ----------------------
    solver = Bisection()

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        solver.solve(lambda x: x, 1.0, 0.0, xtol=1e-9, max_fevals=100)  # a >= b
    with pytest.raises(ValueError):
        solver.solve(lambda x: x, 0.0, 1.0, xtol=0.0, max_fevals=100)  # xtol <= 0
    with pytest.raises(ValueError):
        solver.solve(lambda x: x, 0.0, 1.0, xtol=1e-9, max_fevals=1)  # budget < 2
