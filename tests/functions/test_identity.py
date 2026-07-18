import pytest

from sunnbear.functions import FunctionId, ParamValue


# ==================================================================================================
#  ParamValue
# ==================================================================================================
@pytest.mark.parametrize(
    "pv, expected",
    [
        (ParamValue.decimal(0.2), "0.2"),
        (ParamValue.decimal(1.0), "1.0"),
        (ParamValue.decimal(-0.4), "-0.4"),
        (ParamValue.decimal(6553.6), "6553.6"),
        (ParamValue.exponential(2, 1.2), "2^1.2"),
        (ParamValue.exponential(10, -3.4), "10^-3.4"),
        (ParamValue.exponential(2, 12.3), "2^12.3"),
    ],
)
def test_param_value_rendering(pv, expected):
    assert str(pv) == expected


@pytest.mark.parametrize("token", ["0.2", "1.0", "-0.4", "2^1.2", "10^-3.4", "6553.6", "0.0", "-17.25", "1e-12"])
def test_param_value_parse_render_roundtrip(token):
    assert str(ParamValue.parse(token)) == token


def test_param_value_snap_kills_ulp_noise():
    # --- arrange ----------------------
    noisy = 0.1 + 0.2  # 0.30000000000000004

    # --- act --------------------------
    pv = ParamValue.decimal(noisy)

    # --- assert -----------------------
    assert str(pv) == "0.3"
    assert pv == ParamValue.decimal(0.3)  # identities collapse, not just strings


def test_param_value_snap_applies_to_exponent():
    assert str(ParamValue.exponential(10, -3.4000000000000004)) == "10^-3.4"


def test_param_value_snap_preserves_magnitude():
    # significant digits, not decimal places: tiny values survive
    assert ParamValue.decimal(1e-12).value == 1e-12


def test_param_value_identity_is_by_value_not_notation():
    # --- arrange ----------------------
    as_decimal = ParamValue.decimal(2.0)
    as_pow2 = ParamValue.exponential(2, 1.0)

    # --- act / assert -----------------
    assert as_decimal == as_pow2
    assert hash(as_decimal) == hash(as_pow2)
    assert as_decimal == 2.0  # bare floats compare too


def test_param_value_ordering():
    values = [ParamValue.exponential(2, 2.0), ParamValue.decimal(1.5), ParamValue.decimal(3.0)]
    assert sorted(values) == [ParamValue.decimal(1.5), ParamValue.decimal(3.0), ParamValue.exponential(2, 2.0)]


def test_param_value_rejects_unsupported_base():
    with pytest.raises(ValueError):
        ParamValue.exponential(3, 1.0)


# ==================================================================================================
#  FunctionId
# ==================================================================================================
def test_function_id_canonical_string():
    # --- arrange ----------------------
    fid = FunctionId(formula=105, params=(ParamValue.exponential(2, 1.2), ParamValue.decimal(0.4)))

    # --- act / assert -----------------
    assert str(fid) == "f105-2^1.2_0.4"


def test_function_id_coerces_bare_floats():
    # --- arrange ----------------------
    fid = FunctionId(formula=101, params=(0.2,))

    # --- act / assert -----------------
    assert fid.params == (ParamValue.decimal(0.2),)
    assert fid.param_values == (0.2,)
    assert str(fid) == "f101-0.2"


def test_function_id_no_params():
    assert str(FunctionId(formula=7, params=())) == "f007"


@pytest.mark.parametrize("text", ["f105-2^1.2_0.4", "f007", "f101-0.2", "f102-5.0"])
def test_function_id_string_roundtrip(text):
    assert str(FunctionId.from_string(text)) == text


def test_function_id_ordering():
    # --- arrange ----------------------
    ids = [FunctionId(102, (1.0,)), FunctionId(101, (0.4,)), FunctionId(101, (0.2,))]

    # --- act --------------------------
    ordered = sorted(ids)

    # --- assert -----------------------
    assert ordered == [FunctionId(101, (0.2,)), FunctionId(101, (0.4,)), FunctionId(102, (1.0,))]


@pytest.mark.parametrize("text", ["x101-0.2", "f-abc", "f101-zz", ""])
def test_function_id_from_string_rejects_invalid(text):
    with pytest.raises(ValueError):
        FunctionId.from_string(text)
