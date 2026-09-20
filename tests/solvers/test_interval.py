import pytest
from counted_float import CountedFloat, FlopCountingContext

from sunnbear.solvers import Interval


# ==================================================================================================
#  Invariants
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])  # reversed and degenerate brackets
def test_rejects_ill_ordered_endpoints(a, b):
    with pytest.raises(ValueError, match="a < b"):
        Interval(a, b, -1.0, 1.0)


@pytest.mark.parametrize("fa, fb", [(1.0, 2.0), (-2.0, -1.0), (1.0, -1.0)])  # no sign change, or the wrong way round
def test_rejects_missing_normalized_sign_change(fa, fb):
    with pytest.raises(ValueError, match="fa <= 0 <= fb"):
        Interval(0.0, 1.0, fa, fb)


def test_zero_endpoint_values_are_accepted():
    # --- act --------------------------
    interval = Interval(0.0, 1.0, 0.0, 0.0)

    # --- assert -----------------------
    assert (interval.fa, interval.fb) == (0.0, 0.0)


# ==================================================================================================
#  Geometry
# ==================================================================================================
def test_width_and_midpoint():
    # --- arrange ----------------------
    interval = Interval(1.0, 4.0, -1.0, 2.0)

    # --- act / assert -----------------
    assert interval.width == 3.0
    assert interval.midpoint == 2.5


@pytest.mark.parametrize(
    "fx, expected",
    [
        (-0.5, (1.0, 4.0, -0.5, 2.0)),  # non-positive: x becomes the lower endpoint
        (0.0, (1.0, 4.0, 0.0, 2.0)),  # exact zero: also lower, so the zero endpoint is fa
        (0.5, (0.0, 1.0, -1.0, 0.5)),  # positive: x becomes the upper endpoint
    ],
)
def test_replace_keeps_the_sign_change(fx, expected):
    # --- arrange ----------------------
    interval = Interval(0.0, 4.0, -1.0, 2.0)

    # --- act --------------------------
    narrowed = interval.replace(1.0, fx)

    # --- assert -----------------------
    assert (narrowed.a, narrowed.b, narrowed.fa, narrowed.fb) == expected


# ==================================================================================================
#  Stopping criteria and root extraction
# ==================================================================================================
@pytest.mark.parametrize(
    "interval, two_xtol, expected",
    [
        (Interval(0.0, 1.0, -1.0, 1.0), 1.0, True),  # width criterion: width equal to 2*xtol counts as converged
        (Interval(0.0, 1.0, -1.0, 1.0), 0.5, False),  # width criterion not met, no zero endpoint
        (Interval(0.0, 1.0, 0.0, 1.0), 0.5, True),  # zero-endpoint criterion: lower endpoint is a root
        (Interval(0.0, 1.0, -1.0, 0.0), 0.5, True),  # zero-endpoint criterion: upper endpoint is a root
    ],
)
def test_is_converged(interval, two_xtol, expected):
    assert interval.is_converged(two_xtol) is expected


@pytest.mark.parametrize(
    "interval, expected",
    [
        (Interval(0.0, 1.0, 0.0, 1.0), 0.0),  # zero lower endpoint wins over the midpoint
        (Interval(0.0, 1.0, -1.0, 0.0), 1.0),  # zero upper endpoint wins over the midpoint
        (Interval(0.0, 1.0, -1.0, 1.0), 0.5),  # otherwise the midpoint
    ],
)
def test_root(interval, expected):
    assert interval.root() == expected


# ==================================================================================================
#  Flop accounting
# ==================================================================================================
def test_construction_costs_no_flops_but_geometry_is_counted():
    """The invariant check runs on plain floats; midpoint and width arithmetic on CountedFloat endpoints is counted."""
    # --- arrange ----------------------
    a, b, fa, fb = CountedFloat(0.0), CountedFloat(1.0), CountedFloat(-1.0), CountedFloat(1.0)

    # --- act --------------------------
    with FlopCountingContext() as ctx_construct:
        interval = Interval(a, b, fa, fb)
    with FlopCountingContext() as ctx_geometry:
        _ = interval.midpoint
        _ = interval.width

    # --- assert -----------------------
    assert ctx_construct.flop_counts().total_count() == 0
    assert ctx_geometry.flop_counts().total_count() > 0
