"""This module holds `assert_agrees_with_twin`, the check that every twin test runs."""

import numpy as np

from sunnbear.solvers import Solver, SolveStatus

from .cases import TwinTestCase
from .solver import TwinSolver

# A twin computes the same iterates with its own arithmetic, e.g. a chord's zero computed as a step from one bound,
# so its iterates differ from the solver's by a few ulps; the limit leaves room for that while still catching an
# iterate computed by a different formula, which lies far more ulps away.
MAX_ULPS_APART = 8


def assert_agrees_with_twin(solver: Solver, twin: TwinSolver, test_case: TwinTestCase) -> None:
    """Assert that `solver` and `twin` both converge on `test_case`, through the same evaluated points.

    The check compares the 2 lists of evaluated points pair by pair, with the twin's re-evaluations of the interval
    bounds, which `TwinSolver.n_reevaluated_bounds` declares, left out:

    - each pair of points must lie at most `MAX_ULPS_APART` ulps apart, as `ulps_apart` measures it at the scale
      of the larger of the test case's bounds;
    - the 2 solves evaluate equally many points, and their root estimates lie within `MAX_ULPS_APART`;
    - except when a pair's function values differ in sign: that pair ends the comparison, because the 2 points lie
      so close together that they straddle the root, so rounding decided that sign, and the 2 solves may continue
      differently. Both still converge, so their root estimates lie within ``2 * xtol`` of each other.
    """
    # --- solve ----------------------------------
    sunnbear_result = test_case.solve(solver)
    twin_result = test_case.solve(twin)

    # --- compare --------------------------------
    assert sunnbear_result.status is twin_result.status is SolveStatus.CONVERGED
    twin_history = twin.history_without_reevaluations(twin_result)
    for (sunnbear_x, sunnbear_fx), (twin_x, twin_fx) in zip(sunnbear_result.history, twin_history, strict=False):
        assert ulps_apart(sunnbear_x, twin_x, test_case.scale) <= MAX_ULPS_APART, (
            f"{sunnbear_x!r} and {twin_x!r} differ by more"
        )
        if (sunnbear_fx < 0.0) != (twin_fx < 0.0):
            assert abs(sunnbear_result.x - twin_result.x) <= 2.0 * test_case.xtol
            return
    assert len(sunnbear_result.history) == len(twin_history)
    assert ulps_apart(sunnbear_result.x, twin_result.x, test_case.scale) <= MAX_ULPS_APART


def ulps_apart(x: float, y: float, scale: float) -> float:
    """Return how far apart ``x`` and ``y`` lie, in units of the float64 spacing at the larger of ``|x|``, ``|y|``
    and ``scale``.

    An iterate is computed from the interval bounds, so its rounding error grows with their magnitude, not with its
    own: an iterate close to 0 in an interval of width 1 carries rounding errors of the size of an ulp of 1. The
    caller passes the bounds' magnitude as ``scale``.
    """
    return abs(x - y) / float(np.spacing(max(abs(x), abs(y), scale)))
