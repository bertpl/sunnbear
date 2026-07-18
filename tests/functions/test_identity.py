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


@pytest.mark.parametrize(
    "token, match",
    [
        ("3^1.4", "Unsupported exponent base"),
        ("2^abc", "Malformed exponent"),
        ("zz", "Malformed parameter token"),
    ],
)
def test_param_value_parse_rejects_bad_tokens(token, match):
    with pytest.raises(ValueError, match=match):
        ParamValue.parse(token)


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


def test_param_value_equality_is_notation_sensitive():
    # plain value-object equality; notation-blind identity lives on FunctionId
    assert ParamValue.decimal(2.0) != ParamValue.exponential(2, 1.0)
    assert ParamValue.decimal(2.0).value == ParamValue.exponential(2, 1.0).value


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


def test_function_id_no_params():
    assert str(FunctionId(formula=7, params=())) == "f007"


def test_function_id_equality_is_notation_blind():
    # --- arrange ----------------------
    as_decimal = FunctionId(101, (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId(101, (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert as_decimal == as_pow2
    assert hash(as_decimal) == hash(as_pow2)
    assert len({as_decimal, as_pow2}) == 1  # a set of ids is the whole dedup story


def test_function_id_equality_with_unrelated_type():
    assert FunctionId(101, (ParamValue.decimal(1.0),)) != "f101-1.0"


@pytest.mark.parametrize("text", ["f105-2^1.2_0.4", "f007", "f101-0.2", "f102-5.0"])
def test_function_id_string_roundtrip(text):
    assert str(FunctionId.from_string(text)) == text


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


@pytest.mark.parametrize("text", ["x101-0.2", "f-abc", "f101-zz", ""])
def test_function_id_from_string_rejects_invalid(text):
    with pytest.raises(ValueError):
        FunctionId.from_string(text)
