"""These tests assert that `interval_root_if_converged` applies the stopping criterion of `Interval`."""

import pytest

from sunnbear._core.solvers.core.stopping import interval_root_if_converged
from sunnbear.solvers import Interval


@pytest.mark.parametrize("fa, fb", [(-1.0, 1.0), (0.0, 1.0), (-1.0, 0.0), (1.0, -1.0), (0.0, -1.0), (1.0, 0.0)])
@pytest.mark.parametrize("xtol_doubled", [0.5, 0.6, 1.0])
@pytest.mark.parametrize("is_swapped", [False, True])
def test_the_root_estimate_is_that_of_interval_once_its_criterion_holds(fa, fb, xtol_doubled, is_swapped):
    """For the bounds of an interval in either order, `interval_root_if_converged` returns `Interval.root` bit for bit
    where `Interval.is_converged` holds, and ``None`` where it does not."""
    # --- arrange ----------------------
    interval = Interval.from_interval_bounds(0.1, 0.7, fa, fb)
    if is_swapped:
        bounds = (interval.b, interval.fb, interval.a, interval.fa)
    else:
        bounds = (interval.a, interval.fa, interval.b, interval.fb)
    if interval.is_converged(xtol_doubled):
        expected_root = interval.root()
    else:
        expected_root = None

    # --- act --------------------------
    root = interval_root_if_converged(*bounds, xtol_doubled)

    # --- assert -----------------------
    assert root == expected_root
