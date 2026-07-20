import pytest

from sunnbear.functions import FunctionId, ParamValue


# ==================================================================================================
#  FunctionId
# ==================================================================================================
def test_function_id_display_carries_notation():
    # --- arrange ----------------------
    fid = FunctionId(formula=105, params=(ParamValue.exponential(2, 1.2), ParamValue.decimal(0.4)))

    # --- act / assert -----------------
    assert fid.display() == "f105-2^1.2_0.4"


def test_function_id_rendering_is_faithful():
    """One rendering, carrying the authored notation, so a published identity reproduces exactly."""
    # --- arrange ----------------------
    as_decimal = FunctionId(101, (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId(101, (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert str(as_decimal) == "f101-4.0"
    assert str(as_pow2) == "f101-2^2.0"  # not flattened to the decimal spelling
    assert repr(as_pow2) == str(as_pow2) == as_pow2.display()


def test_function_id_no_params():
    assert str(FunctionId(formula=7, params=())) == "f007"


def test_function_id_equality_is_exact():
    """Equality stays a real equivalence over exact values; collapsing near-matches happens earlier."""
    # --- arrange ----------------------
    as_decimal = FunctionId(101, (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId(101, (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert as_decimal != as_pow2  # same number, different notation: two identities
    assert len({as_decimal, as_pow2}) == 2
    assert as_decimal == FunctionId(101, (ParamValue.decimal(4.0),))  # and reflexive on equal spellings


def test_function_id_equality_with_unrelated_type():
    assert FunctionId(101, (ParamValue.decimal(1.0),)) != "f101-1.0"


@pytest.mark.parametrize("text", ["f105-2^1.2_0.4", "f007", "f101-0.2", "f102-5.0"])
def test_function_id_display_roundtrip(text):
    assert FunctionId.from_string(text).display() == text


@pytest.mark.parametrize("text", ["f105-2^1.2_0.4", "f007", "f101-0.2", "f102-5.0"])
def test_function_id_canonical_form_reparses_to_the_same_identity(text):
    original = FunctionId.from_string(text)
    assert FunctionId.from_string(str(original)) == original


def test_function_id_ordering():
    # --- arrange ----------------------
    ids = [
        FunctionId(102, (ParamValue.decimal(1.0),)),
        FunctionId(101, (ParamValue.decimal(0.4),)),
        FunctionId(101, (ParamValue.decimal(0.2),)),
    ]

    # --- act --------------------------
    ordered = sorted(ids)

    # --- assert -----------------------
    assert [str(fid) for fid in ordered] == ["f101-0.2", "f101-0.4", "f102-1.0"]


@pytest.mark.parametrize("text", ["x101-0.2", "f-abc", "f101-zz", "", "f101-"])
def test_function_id_from_string_rejects_invalid(text):
    with pytest.raises(ValueError):
        FunctionId.from_string(text)
