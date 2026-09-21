"""`SolverState` counts iterations only once a solver marks one."""

from sunnbear._core.solvers.core.wrapped_function import WrappedFunction
from sunnbear.solvers import Interval, SolverState


def _state() -> SolverState:
    wf = WrappedFunction(lambda x: x - 0.5, max_fevals=10, record_history=False)
    return SolverState(f=wf, bracket=Interval.from_endpoints(0.0, 1.0, -0.5, 0.5), xtol=1e-3)


def test_iterations_are_none_until_the_first_mark():
    # --- arrange ----------------------
    state = _state()

    # --- act --------------------------
    before = state.n_iters
    state.incr_iteration_count()
    state.incr_iteration_count()

    # --- assert -----------------------
    assert (before, state.n_iters) == (None, 2)
