import pytest
from counted_float import CountedFloat, FlopCountingContext, FlopCounts

from sunnbear.solvers import DecreasingInterval, IncreasingInterval, Interval, IntervalBound

ORIENTATIONS = [IncreasingInterval, DecreasingInterval]


def test_orientations_cover_every_interval_subclass():
    """Assert ORIENTATIONS names every concrete subclass of Interval."""
    assert set(ORIENTATIONS) == set(Interval.__subclasses__())


def _orient_values_at_interval_bounds(cls: type[Interval], fa: float, fb: float) -> tuple[float, float]:
    """Return the values at the interval bounds as given for the increasing orientation, negated for decreasing."""
    return (fa, fb) if cls is IncreasingInterval else (-fa, -fb)


# ==================================================================================================
#  Invariants
# ==================================================================================================
# ==================================================================================================
#  Construction from the function values at the interval bounds
# ==================================================================================================
@pytest.mark.parametrize(
    "fa, fb, cls_expected",
    [
        (-1.0, 1.0, IncreasingInterval),
        (1.0, -1.0, DecreasingInterval),
        (0.0, 1.0, IncreasingInterval),  # a zero at the lower interval bound with the other positive at b: rises
        (1.0, 0.0, DecreasingInterval),  # a zero at the upper interval bound with the other positive at a: falls
        (0.0, 0.0, IncreasingInterval),  # both zero holds either; the increasing class is the default
    ],
)
def test_from_interval_bounds_picks_the_orientation(fa, fb, cls_expected):
    # --- act --------------------------
    interval = Interval.from_interval_bounds(0.0, 1.0, fa, fb)

    # --- assert -----------------------
    assert type(interval) is cls_expected
    assert (interval.a, interval.b, interval.fa, interval.fb) == (0.0, 1.0, fa, fb)
    assert interval.last_replaced_bound is None  # The initial interval was not produced by a split.


@pytest.mark.parametrize("fa, fb", [(1.0, 2.0), (-2.0, -1.0)])
def test_from_interval_bounds_rejects_a_missing_sign_change(fa, fb):
    with pytest.raises(ValueError, match="differ in sign"):
        Interval.from_interval_bounds(0.0, 1.0, fa, fb)


# ==================================================================================================
#  Geometry
# ==================================================================================================
@pytest.mark.parametrize("cls", ORIENTATIONS)
def test_width_and_midpoint(cls):
    # --- arrange ----------------------
    interval = cls(1.0, 4.0, *_orient_values_at_interval_bounds(cls, -1.0, 2.0))

    # --- act / assert -----------------
    assert interval.width == 3.0
    assert interval.midpoint == 2.5


@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fx, expected, replaced_expected",
    [
        (-0.5, (1.0, 4.0, -0.5, 2.0), IntervalBound.LOWER),  # the sign of fa: x becomes the lower interval bound
        (0.0, (1.0, 4.0, 0.0, 2.0), IntervalBound.LOWER),  # exact zero: also lower, so the zero interval bound is fa
        (0.5, (0.0, 1.0, -1.0, 0.5), IntervalBound.UPPER),  # the sign of fb: x becomes the upper interval bound
    ],
)
def test_split_at_keeps_the_sign_change_and_the_orientation(cls, fx, expected, replaced_expected):
    # --- arrange ----------------------
    interval = cls(0.0, 4.0, *_orient_values_at_interval_bounds(cls, -1.0, 2.0))
    a_expected, b_expected, fa_expected, fb_expected = expected

    # --- act --------------------------
    narrowed = interval.split_at(1.0, _orient_values_at_interval_bounds(cls, fx, 0.0)[0])

    # --- assert -----------------------
    assert type(narrowed) is cls
    assert (narrowed.a, narrowed.b) == (a_expected, b_expected)
    assert (narrowed.fa, narrowed.fb) == _orient_values_at_interval_bounds(cls, fa_expected, fb_expected)
    assert narrowed.last_replaced_bound is replaced_expected


# ==================================================================================================
#  Stopping criteria and root extraction
# ==================================================================================================
@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fa, fb, two_xtol, expected",
    [
        (-1.0, 1.0, 1.0, True),  # width criterion: width equal to 2*xtol counts as converged
        (-1.0, 1.0, 0.5, False),  # the width criterion is not met and no interval bound is zero
        (0.0, 1.0, 0.5, True),  # zero-bound criterion: the lower interval bound is a root
        (-1.0, 0.0, 0.5, True),  # zero-bound criterion: the upper interval bound is a root
    ],
)
def test_is_converged(cls, fa, fb, two_xtol, expected):
    assert cls(0.0, 1.0, *_orient_values_at_interval_bounds(cls, fa, fb)).is_converged(two_xtol) is expected


@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fa, fb, expected",
    [
        (0.0, 1.0, 0.0),  # a zero lower interval bound wins over the midpoint
        (-1.0, 0.0, 1.0),  # a zero upper interval bound wins over the midpoint
        (-1.0, 1.0, 0.5),  # the midpoint is returned otherwise
    ],
)
def test_root(cls, fa, fb, expected):
    assert cls(0.0, 1.0, *_orient_values_at_interval_bounds(cls, fa, fb)).root() == expected


# ==================================================================================================
#  Flop accounting
# ==================================================================================================
def test_the_sign_checks_and_the_geometry_are_counted_on_counted_interval_bounds():
    # --- arrange ----------------------
    a, b, fa, fb = CountedFloat(0.0), CountedFloat(1.0), CountedFloat(-1.0), CountedFloat(1.0)

    # --- act --------------------------
    with FlopCountingContext() as ctx_construct:
        interval = Interval.from_interval_bounds(a, b, fa, fb)
    with FlopCountingContext() as ctx_geometry:
        _ = interval.midpoint
        _ = interval.width

    # --- assert -----------------------
    assert ctx_construct.flop_counts() == FlopCounts(COMP=2)  # The increasing orientation's two comparisons.
    assert ctx_geometry.flop_counts() == FlopCounts(ADD=1, MUL=1, SUB=1)
