"""The foundation layers work end to end: registry, test function, both solvers, flop counts, summary statistic."""

import numpy as np

from sunnbear import FormulaRegistry, SolveStatus
from sunnbear.solvers import Bisection, RegulaFalsi
from sunnbear.stats import gpq

MAX_FEVALS = 200


def test_solve_count_flops_summarize():
    """A test function from the registry is solved over a batch of c-values; the counts feed a pseudo-quantile."""
    # --- arrange ----------------------
    test_function = FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0)
    c_values = np.linspace(test_function.c_min, test_function.c_max, 9)[1:-1]
    solvers = [Bisection(), RegulaFalsi()]

    # --- act --------------------------
    n_fevals = {solver.name: [] for solver in solvers}
    statuses = {solver.name: [] for solver in solvers}
    for solver in solvers:
        for c in c_values:
            f = test_function.build_x_fun(float(c))
            result = solver.solve(f, test_function.a, test_function.b, xtol=1e-8, max_fevals=MAX_FEVALS)
            assert result.flop_counts.total_count() > 0
            n_fevals[solver.name].append(result.n_fevals)
            statuses[solver.name].append(result.status)

    # --- assert -----------------------
    assert all(status is SolveStatus.CONVERGED for status in statuses["bisection"])
    # Regula falsi's retained endpoint stalls on some c-values, which is the budget path the milestone covers.
    assert SolveStatus.MAX_FEVALS in statuses["regula_falsi"]
    stalled = [
        n
        for n, s in zip(n_fevals["regula_falsi"], statuses["regula_falsi"], strict=True)
        if s is SolveStatus.MAX_FEVALS
    ]
    assert all(n == MAX_FEVALS for n in stalled)
    counts = n_fevals["bisection"]
    assert 2 < gpq(counts, 0.5) <= gpq(counts, 0.9) <= max(counts)
