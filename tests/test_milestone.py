"""End-to-end milestone: registry -> test function -> solve -> flops -> summary statistic.

Exercises the full foundation-layer chain on the example corpus: materialize
a test function from its identity, bind Monte-Carlo parameter values, solve
with both reference solvers inside flop counting, and summarize the resulting
evaluation counts with a geometric pseudo-quantile. Both termination regimes
are part of the milestone: bisection converges everywhere, while pure regula
falsi's endpoint-retention stall exercises the budget-capped path.
"""

import numpy as np

from sunnbear import Bisection, RegulaFalsi, SolveStatus, build
from sunnbear.stats import gpq

MAX_FEVALS = 200


def test_solve_count_flops_summarize():
    # --- arrange ----------------------
    test_function = build("f101-0.2", c_range=(-5.0, 5.0))
    c_values = np.linspace(test_function.c_min, test_function.c_max, 9)[1:-1]
    solvers = [Bisection(), RegulaFalsi()]

    # --- act --------------------------
    n_fevals: dict[str, list[int]] = {}
    statuses: dict[str, list[SolveStatus]] = {}
    for solver in solvers:
        for c in c_values:
            result = solver.solve(
                test_function.bind(float(c)),
                test_function.a,
                test_function.b,
                xtol=1e-8,
                max_fevals=MAX_FEVALS,
            )
            assert result.flop_counts.total_count() > 0  # solver arithmetic was counted
            n_fevals.setdefault(solver.name, []).append(result.n_fevals)
            statuses.setdefault(solver.name, []).append(result.status)

    # --- assert -----------------------
    # bisection: converged everywhere, within tolerance of a true root
    assert all(status == SolveStatus.CONVERGED for status in statuses["bisection"])
    # regula falsi: the endpoint-retention stall shows up on this curved cubic
    assert SolveStatus.MAX_FEVALS in statuses["regula_falsi"]
    assert all(n == MAX_FEVALS for n, s in zip(n_fevals["regula_falsi"], statuses["regula_falsi"], strict=True) if s == SolveStatus.MAX_FEVALS)
    # summary statistics over the evaluation counts
    counts = n_fevals["bisection"]
    assert 2 < gpq(counts, 0.5) <= gpq(counts, 0.9) <= max(counts)
