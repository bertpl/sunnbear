"""This test drives the package's 3 layers through each other: solve a shipped function, count flops, compute a gpq.

The benchmark engine will run this loop at scale; here it runs once, with the smallest inputs, so
a mismatch in the contracts between the layers surfaces before the engine exists.
"""

import numpy as np
import pytest

from sunnbear.functions import FormulaRegistry
from sunnbear.solvers import Bisection, RegulaFalsi, SolveStatus
from sunnbear.stats import gpq

C_VALUES = np.linspace(-1.0, 1.0, 5)  # A batch of shifts, all inside the calibrated c-range below.


@pytest.fixture(scope="module")
def cubic():
    """Return the shipped cubic, ``x^3 - 0.2 x - c`` on ``[-2, 2]``, calibrated to ``c`` in ``[-1, 1]``."""
    return FormulaRegistry.candidate_from_id("f101-0.2").calibrated(c_min=-1.0, c_max=1.0)


def test_a_shipped_function_is_solved_by_both_solvers_with_counted_flops(cubic):
    # --- act --------------------------
    results = {
        solver.name: [solver.solve(cubic.build_x_fun(c), cubic.a, cubic.b, xtol=1e-9, max_fevals=200) for c in C_VALUES]
        for solver in (Bisection(), RegulaFalsi())
    }

    # --- assert -----------------------
    for name, batch in results.items():
        for c, result in zip(C_VALUES, batch, strict=True):
            assert result.status in (SolveStatus.CONVERGED, SolveStatus.MAX_FEVALS), (name, c, result.status)
            assert result.flop_counts.total_count() > 0, (name, c)
            assert cubic.a <= result.x <= cubic.b, (name, c)
    for c, result in zip(C_VALUES, results["bisection"], strict=True):
        assert result.status is SolveStatus.CONVERGED
        # The slope on the interval is at most 12, so the residual at a converged estimate is small.
        assert abs(cubic.build_x_fun(c)(result.x)) < 1e-6


def test_a_gpq_over_a_batch_of_evaluation_counts(cubic):
    # --- act --------------------------
    n_fevals = [
        Bisection().solve(cubic.build_x_fun(c), cubic.a, cubic.b, xtol=1e-6, max_fevals=200).n_fevals for c in C_VALUES
    ]
    cost = gpq(n_fevals, 0.5)

    # --- assert -----------------------
    # At level 0.5 the gpq is the geometric mean. The batch is not uniform: c = 0 has its root at the first midpoint.
    assert min(n_fevals) < max(n_fevals)
    assert cost == pytest.approx(float(np.exp(np.mean(np.log(n_fevals)))))
