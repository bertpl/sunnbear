"""`SolveRun` counts iterations only once a solver marks one."""

from sunnbear._core.solvers.core.wrapped_function import WrappedFunction
from sunnbear.solvers import Interval, SolveRun


def _run() -> SolveRun:
    wf = WrappedFunction(lambda x: x - 0.5, 0.0, 1.0, max_fevals=10, record_history=False)
    return SolveRun(f=wf, bracket=Interval(0.0, 1.0, -0.5, 0.5), xtol=1e-3)


def test_iterations_are_none_until_the_first_mark():
    # --- arrange ----------------------
    run = _run()

    # --- act --------------------------
    before = run.n_iters
    run.mark_iteration()
    run.mark_iteration()

    # --- assert -----------------------
    assert (before, run.n_iters) == (None, 2)
