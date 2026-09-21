import pytest
from counted_float import CountedFloat, FlopCountingContext

from sunnbear.solvers import DecreasingInterval, IncreasingInterval, Interval

ORIENTATIONS = [IncreasingInterval, DecreasingInterval]


def test_orientations_cover_every_interval_subclass():
    """Assert ORIENTATIONS names every concrete subclass of Interval, so a new orientation is not missed here."""
    assert set(ORIENTATIONS) == set(Interval.__subclasses__())


def _orient_endpoints(cls: type[Interval], fa: float, fb: float) -> tuple[float, float]:
    """Return ``(fa, fb)`` as given for the increasing orientation and negated for the decreasing one."""
    return (fa, fb) if cls is IncreasingInterval else (-fa, -fb)


# ==================================================================================================
#  Invariants
# ==================================================================================================
@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize("a, b", [(1.0, -1.0), (0.0, 0.0)])  # the first pair is reversed, the second is degenerate
def test_rejects_ill_ordered_endpoints(cls, a, b):
    with pytest.raises(ValueError, match="a < b"):
        cls(a, b, *_orient_endpoints(cls, -1.0, 1.0))


@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize("fa, fb", [(1.0, 2.0), (-2.0, -1.0), (1.0, -1.0)])  # no sign change, or the wrong way round
def test_rejects_endpoint_values_of_the_wrong_orientation(cls, fa, fb):
    with pytest.raises(ValueError, match=cls.__name__):
        cls(0.0, 1.0, *_orient_endpoints(cls, fa, fb))


@pytest.mark.parametrize("cls", ORIENTATIONS)
def test_zero_endpoint_values_are_accepted(cls):
    # --- act --------------------------
    interval = cls(0.0, 1.0, 0.0, 0.0)

    # --- assert -----------------------
    assert (interval.fa, interval.fb) == (0.0, 0.0)


# ==================================================================================================
#  Construction from endpoint values
# ==================================================================================================
@pytest.mark.parametrize(
    "fa, fb, cls_expected",
    [
        (-1.0, 1.0, IncreasingInterval),
        (1.0, -1.0, DecreasingInterval),
        (0.0, 1.0, IncreasingInterval),  # a zero endpoint with the other positive at b: rises
        (1.0, 0.0, DecreasingInterval),  # a zero endpoint with the other positive at a: falls
        (0.0, 0.0, IncreasingInterval),  # both zero holds either; the increasing class is the default
    ],
)
def test_from_endpoints_picks_the_orientation(fa, fb, cls_expected):
    # --- act --------------------------
    interval = Interval.from_endpoints(0.0, 1.0, fa, fb)

    # --- assert -----------------------
    assert type(interval) is cls_expected
    assert (interval.a, interval.b, interval.fa, interval.fb) == (0.0, 1.0, fa, fb)


@pytest.mark.parametrize("fa, fb", [(1.0, 2.0), (-2.0, -1.0)])
def test_from_endpoints_rejects_a_missing_sign_change(fa, fb):
    with pytest.raises(ValueError, match="differ in sign"):
        Interval.from_endpoints(0.0, 1.0, fa, fb)


# ==================================================================================================
#  Geometry
# ==================================================================================================
@pytest.mark.parametrize("cls", ORIENTATIONS)
def test_width_and_midpoint(cls):
    # --- arrange ----------------------
    interval = cls(1.0, 4.0, *_orient_endpoints(cls, -1.0, 2.0))

    # --- act / assert -----------------
    assert interval.width == 3.0
    assert interval.midpoint == 2.5


@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fx, expected",
    [
        (-0.5, (1.0, 4.0, -0.5, 2.0)),  # the sign of fa: x becomes the lower endpoint
        (0.0, (1.0, 4.0, 0.0, 2.0)),  # exact zero: also lower, so the zero endpoint is fa
        (0.5, (0.0, 1.0, -1.0, 0.5)),  # the sign of fb: x becomes the upper endpoint
    ],
)
def test_split_at_keeps_the_sign_change_and_the_orientation(cls, fx, expected):
    # --- arrange ----------------------
    interval = cls(0.0, 4.0, *_orient_endpoints(cls, -1.0, 2.0))
    a_expected, b_expected, fa_expected, fb_expected = expected

    # --- act --------------------------
    narrowed = interval.split_at(1.0, _orient_endpoints(cls, fx, 0.0)[0])

    # --- assert -----------------------
    assert type(narrowed) is cls
    assert (narrowed.a, narrowed.b) == (a_expected, b_expected)
    assert (narrowed.fa, narrowed.fb) == _orient_endpoints(cls, fa_expected, fb_expected)


# ==================================================================================================
#  Stopping criteria and root extraction
# ==================================================================================================
@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fa, fb, two_xtol, expected",
    [
        (-1.0, 1.0, 1.0, True),  # width criterion: width equal to 2*xtol counts as converged
        (-1.0, 1.0, 0.5, False),  # the width criterion is not met and no endpoint is zero
        (0.0, 1.0, 0.5, True),  # zero-endpoint criterion: lower endpoint is a root
        (-1.0, 0.0, 0.5, True),  # zero-endpoint criterion: upper endpoint is a root
    ],
)
def test_is_converged(cls, fa, fb, two_xtol, expected):
    assert cls(0.0, 1.0, *_orient_endpoints(cls, fa, fb)).is_converged(two_xtol) is expected


@pytest.mark.parametrize("cls", ORIENTATIONS)
@pytest.mark.parametrize(
    "fa, fb, expected",
    [
        (0.0, 1.0, 0.0),  # zero lower endpoint wins over the midpoint
        (-1.0, 0.0, 1.0),  # zero upper endpoint wins over the midpoint
        (-1.0, 1.0, 0.5),  # the midpoint is returned otherwise
    ],
)
def test_root(cls, fa, fb, expected):
    assert cls(0.0, 1.0, *_orient_endpoints(cls, fa, fb)).root() == expected


# ==================================================================================================
#  Flop accounting
# ==================================================================================================
def test_construction_costs_no_flops_but_geometry_is_counted():
    """The invariant checks run on plain floats; midpoint and width arithmetic on CountedFloat endpoints is counted."""
    # --- arrange ----------------------
    a, b, fa, fb = CountedFloat(0.0), CountedFloat(1.0), CountedFloat(-1.0), CountedFloat(1.0)

    # --- act --------------------------
    with FlopCountingContext() as ctx_construct:
        interval = Interval.from_endpoints(a, b, fa, fb)
    with FlopCountingContext() as ctx_geometry:
        _ = interval.midpoint
        _ = interval.width

    # --- assert -----------------------
    assert ctx_construct.flop_counts().total_count() == 0
    assert ctx_geometry.flop_counts().total_count() > 0
