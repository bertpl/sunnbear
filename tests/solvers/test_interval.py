import pytest

from sunnbear.solvers import Interval


def test_interval_properties():
    # --- arrange ----------------------
    iv = Interval(a=1.0, b=3.0, fa=-2.0, fb=4.0)

    # --- act / assert -----------------
    assert iv.width == pytest.approx(2.0)
    assert iv.midpoint == pytest.approx(2.0)


@pytest.mark.parametrize(
    "a, b, fa, fb",
    [
        (3.0, 1.0, -1.0, 1.0),  # a >= b
        (1.0, 3.0, 1.0, 2.0),  # fa > 0
        (1.0, 3.0, -2.0, -1.0),  # fb < 0
    ],
)
def test_interval_rejects_invalid(a, b, fa, fb):
    with pytest.raises(ValueError):
        Interval(a=a, b=b, fa=fa, fb=fb)


def test_replace_keeps_sign_change():
    # --- arrange ----------------------
    iv = Interval(a=0.0, b=4.0, fa=-1.0, fb=3.0)

    # --- act --------------------------
    replaced_low = iv.replace(2.0, -0.5)  # fx <= 0: replaces a
    replaced_high = iv.replace(2.0, 0.5)  # fx > 0: replaces b

    # --- assert -----------------------
    assert (replaced_low.a, replaced_low.b, replaced_low.fa, replaced_low.fb) == (2.0, 4.0, -0.5, 3.0)
    assert (replaced_high.a, replaced_high.b, replaced_high.fa, replaced_high.fb) == (0.0, 2.0, -1.0, 0.5)


def test_replace_with_exact_zero_lands_on_a():
    # --- arrange ----------------------
    iv = Interval(a=0.0, b=4.0, fa=-1.0, fb=3.0)

    # --- act --------------------------
    replaced = iv.replace(2.0, 0.0)

    # --- assert -----------------------
    assert (replaced.a, replaced.fa) == (2.0, 0.0)
