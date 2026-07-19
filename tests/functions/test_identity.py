import pytest

from sunnbear.functions import DecimalParamValue, ExponentialParamValue, FunctionId, ParamValue


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
def test_param_value_display_carries_notation(pv, expected):
    assert pv.display() == expected


@pytest.mark.parametrize(
    "pv, expected",
    [
        (ParamValue.decimal(0.2), "0.2"),
        (ParamValue.exponential(2, 2.0), "4.0"),  # notation gone: canonical is plain decimal
        (ParamValue.exponential(10, 1.0), "10.0"),
    ],
)
def test_param_value_str_is_canonical(pv, expected):
    assert str(pv) == expected
    assert repr(pv) == expected  # repr matches str: equal values print equally


def test_param_value_str_is_notation_blind():
    assert str(ParamValue.decimal(4.0)) == str(ParamValue.exponential(2, 2.0))


@pytest.mark.parametrize("token", ["0.2", "1.0", "-0.4", "2^1.2", "10^-3.4", "6553.6", "0.0", "-17.25", "1e-12"])
def test_param_value_parse_display_roundtrip(token):
    assert ParamValue.parse(token).display() == token


@pytest.mark.parametrize("token", ["0.2", "2^1.2", "10^-3.4", "2^12.3", "1e-12", "-17.25"])
def test_param_value_canonical_form_reparses_to_the_same_value(token):
    """The canonical rendering is what storage keys on, so it must survive a round-trip exactly."""
    original = ParamValue.parse(token)
    assert ParamValue.parse(str(original)).value == original.value


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
    assert ParamValue.exponential(10, -3.4000000000000004).display() == "10^-3.4"


def test_param_value_snap_preserves_magnitude():
    # significant digits, not decimal places: tiny values survive
    assert ParamValue.decimal(1e-12).value == 1e-12


def test_param_value_equality_is_notation_sensitive():
    # plain value-object equality; notation-blind identity lives on FunctionId
    assert ParamValue.decimal(2.0) != ParamValue.exponential(2, 1.0)
    assert ParamValue.decimal(2.0).value == ParamValue.exponential(2, 1.0).value


@pytest.mark.parametrize(
    "pv, expected_type",
    [
        (ParamValue.decimal(0.2), DecimalParamValue),
        (ParamValue.parse("0.2"), DecimalParamValue),
        (ParamValue.exponential(2, 1.2), ExponentialParamValue),
        (ParamValue.parse("2^1.2"), ExponentialParamValue),
    ],
)
def test_factories_build_the_matching_variant(pv, expected_type):
    assert isinstance(pv, expected_type)


def test_decimal_variant_carries_no_notation_fields():
    """Illegal states are unrepresentable: a decimal value has no base/exponent to be wrong."""
    assert not hasattr(ParamValue.decimal(4.0), "base")
    assert not hasattr(ParamValue.decimal(4.0), "exponent")


@pytest.mark.parametrize(
    "pv",
    [
        DecimalParamValue(value=0.1 + 0.2),  # constructed directly, bypassing the factory
        ExponentialParamValue(value=2**0.5, base=2, exponent=0.5),
        ParamValue.decimal(0.1 + 0.2),
        ParamValue.exponential(2, 12.3),
    ],
)
def test_value_is_canonical_on_every_construction_path(pv):
    """The base class enforces the invariant, so no variant can forget to apply it."""
    assert pv.value == float(f"{pv.value:.10g}")
    assert ParamValue.parse(str(pv)).value == pv.value  # and therefore the canonical form round-trips


@pytest.mark.parametrize("base", [3, 2.5, 0, -2])
def test_param_value_rejects_unsupported_base(base):
    """2.5 matters: it guards against the int() normalization silently truncating a bad base to 2."""
    with pytest.raises(ValueError):
        ParamValue.exponential(base, 1.0)


@pytest.mark.parametrize("base", [2, 2.0, 10, 10.0])
def test_exponential_accepts_int_or_float_base(base):
    """A float 2.0/10.0 is a valid base, normalized to int so display and identity stay clean."""
    # --- act --------------------------
    pv = ParamValue.exponential(base, 1.0)

    # --- assert -----------------------
    assert pv.display() == f"{int(base)}^1.0"  # int base, no "2.0^..." leakage


# ==================================================================================================
#  FunctionId
# ==================================================================================================
def test_function_id_display_carries_notation():
    # --- arrange ----------------------
    fid = FunctionId(formula=105, params=(ParamValue.exponential(2, 1.2), ParamValue.decimal(0.4)))

    # --- act / assert -----------------
    assert fid.display() == "f105-2^1.2_0.4"


def test_function_id_str_is_canonical_and_notation_blind():
    """Storage keys on str(), so two spellings of one identity must give one string."""
    # --- arrange ----------------------
    as_decimal = FunctionId(101, (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId(101, (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert str(as_decimal) == str(as_pow2) == "f101-4.0"
    assert repr(as_decimal) == str(as_decimal)  # repr matches str
    assert as_pow2.display() == "f101-2^2.0"  # the authored notation survives, for humans


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


def test_function_id_dedup_survives_inexact_exponent():
    """A log grid's exponent can carry float noise; canonicalization must still fold it onto the decimal value."""
    # --- arrange ----------------------
    noisy = FunctionId(101, (ParamValue.exponential(2, 2.0 + 1e-11),))  # 2^~2.0 -> ~4.0
    exact = FunctionId(101, (ParamValue.decimal(4.0),))

    # --- act / assert -----------------
    assert noisy.param_values == (4.0,)  # canonicalized despite the noisy exponent
    assert noisy == exact
    assert hash(noisy) == hash(exact)
    assert len({noisy, exact}) == 1


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


@pytest.mark.parametrize("text", ["x101-0.2", "f-abc", "f101-zz", ""])
def test_function_id_from_string_rejects_invalid(text):
    with pytest.raises(ValueError):
        FunctionId.from_string(text)
