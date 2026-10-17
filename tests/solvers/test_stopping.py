"""These tests assert that `is_interval_converged` and `interval_root` apply the stopping criterion of `Interval`."""

import pytest

from sunnbear._core.solvers.core.stopping import interval_root, is_interval_converged
from sunnbear.solvers import Interval


@pytest.mark.parametrize("fa, fb", [(-1.0, 1.0), (0.0, 1.0), (-1.0, 0.0), (1.0, -1.0), (0.0, -1.0), (1.0, 0.0)])
@pytest.mark.parametrize("xtol_doubled", [0.5, 0.6, 1.0])
@pytest.mark.parametrize("is_swapped", [False, True])
def test_the_criterion_and_the_root_estimate_are_those_of_interval(fa, fb, xtol_doubled, is_swapped):
    """For the bounds of an interval in either order, `is_interval_converged` and `interval_root` return what
    `Interval.is_converged` and `Interval.root` return for that interval, bit for bit."""
    # --- arrange ----------------------
    interval = Interval.from_interval_bounds(0.1, 0.7, fa, fb)
    if is_swapped:
        bounds = (interval.b, interval.fb, interval.a, interval.fa)
    else:
        bounds = (interval.a, interval.fa, interval.b, interval.fb)

    # --- act / assert -----------------
    assert is_interval_converged(*bounds, xtol_doubled) is interval.is_converged(xtol_doubled)
    assert interval_root(*bounds) == interval.root()
