import pytest

from sunnbear.functions import (
    DecimalParamValue,
    ExponentialParamValue,
    FunctionId,
    ParamValue,
    deduplicate_ids,
)


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
        (ParamValue.exponential(2, 2.0), "2^2.0"),  # the authored notation survives
        (ParamValue.exponential(10, 1.0), "10^1.0"),
    ],
)
def test_param_value_renders_its_authored_notation(pv, expected):
    """There is one rendering, and it is faithful — str, repr and display all agree."""
    assert str(pv) == expected
    assert repr(pv) == expected
    assert pv.display() == expected


def test_param_value_rendering_is_notation_sensitive():
    """Two spellings of the same number render differently; collapsing them is the filter's job."""
    # --- arrange ----------------------
    as_decimal = ParamValue.decimal(4.0)
    as_pow2 = ParamValue.exponential(2, 2.0)

    # --- act / assert -----------------
    assert str(as_decimal) != str(as_pow2)
    assert as_decimal.value == as_pow2.value  # same number, different notation


@pytest.mark.parametrize("token", ["0.2", "1.0", "-0.4", "2^1.2", "10^-3.4", "6553.6", "0.0", "-17.25", "1e-12"])
def test_param_value_parse_display_roundtrip(token):
    assert ParamValue.parse(token).display() == token


@pytest.mark.parametrize("token", ["0.2", "2^1.2", "10^-3.4", "2^12.3", "1e-12", "-17.25"])
def test_param_value_rendering_reparses_to_the_same_value(token):
    """A published parameter must come back as the same float, or reproducing results is guesswork."""
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
        ParamValue.decimal(0.1 + 0.2),
    ],
)
def test_decimal_snaps_its_value(pv):
    """For a linear grid the value *is* the swept quantity, so that is what absorbs the float error."""
    assert pv.value == float(f"{pv.value:.10g}")


@pytest.mark.parametrize(
    "pv",
    [
        ExponentialParamValue(value=0.0, base=2, exponent=0.5),  # value is derived, never trusted
        ParamValue.exponential(2, 12.3),
        ParamValue.exponential(10, -3.4000000000000004),
    ],
)
def test_exponential_snaps_its_exponent_and_derives_the_value(pv):
    """For a log grid the exponent is the swept quantity; the value follows from it untouched."""
    assert pv.exponent == float(f"{pv.exponent:.10g}")
    assert pv.value == float(pv.base) ** pv.exponent  # derived exactly, not rounded


def test_exponential_value_is_exactly_reproducible():
    """The point of the whole scheme: computing 2 ** 1.23 yourself gives the number sunnbear used."""
    assert ParamValue.exponential(2, 1.23).value == 2**1.23


def test_param_value_equality_with_unrelated_type():
    assert ParamValue.decimal(1.0) != "1.0"


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


def test_exponential_variant_validates_base_on_direct_construction():
    """The factory is not the only way in, so the base invariant lives on the variant itself."""
    with pytest.raises(ValueError):
        ExponentialParamValue(value=8.0, base=3, exponent=2.0)


@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_param_value_rejects_non_finite(bad):
    """A NaN identity would quietly break equality, hashing and dedup, so every path rejects it."""
    with pytest.raises(ValueError, match="finite"):
        ParamValue.decimal(bad)
    with pytest.raises(ValueError, match="finite"):
        ParamValue.exponential(2, bad)
    with pytest.raises(ValueError, match="finite"):
        DecimalParamValue(value=bad)  # direct construction, bypassing the factory
    with pytest.raises(ValueError, match="finite"):
        ExponentialParamValue(value=1.0, base=2, exponent=bad)


@pytest.mark.parametrize("token", ["inf", "-inf", "nan", "2^inf", "10^nan"])
def test_param_value_parse_rejects_non_finite_tokens(token):
    with pytest.raises(ValueError):
        ParamValue.parse(token)


def test_exponential_rejects_overflowing_derivation():
    """A finite exponent can still overflow base**exponent; the derived value is checked too."""
    with pytest.raises(ValueError, match="non-finite"):
        ParamValue.exponential(10, 400.0)


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
    """Equality stays a real equivalence over exact values; collapsing near-matches is a separate pass."""
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


# ==================================================================================================
#  deduplicate_ids
# ==================================================================================================
def test_deduplicate_ids_collapses_notations_of_one_value():
    # --- arrange ----------------------
    ids = [
        FunctionId(101, (ParamValue.decimal(4.0),)),
        FunctionId(101, (ParamValue.exponential(2, 2.0),)),
    ]

    # --- act --------------------------
    kept = deduplicate_ids(ids)

    # --- assert -----------------------
    assert [str(fid) for fid in kept] == ["f101-4.0"]


def test_deduplicate_ids_collapses_a_near_match():
    """Values differing past the granularity are one function — which exact equality cannot express."""
    # --- arrange ----------------------
    exact = FunctionId(101, (ParamValue.decimal(4.0),))
    nearly = FunctionId(101, (ParamValue.exponential(2, 2.000000001),))  # 2^~2 -> 4.00000000277

    # --- act / assert -----------------
    assert nearly.param_values != exact.param_values  # genuinely different floats
    assert nearly != exact
    assert len(deduplicate_ids([exact, nearly])) == 1


def test_deduplicate_ids_is_first_come_first_served():
    # --- arrange ----------------------
    as_pow2 = FunctionId(101, (ParamValue.exponential(2, 2.0),))
    as_decimal = FunctionId(101, (ParamValue.decimal(4.0),))

    # --- act / assert -----------------
    assert deduplicate_ids([as_pow2, as_decimal]) == (as_pow2,)
    assert deduplicate_ids([as_decimal, as_pow2]) == (as_decimal,)


@pytest.mark.parametrize("digits, n_kept", [(8, 1), (12, 2)])
def test_deduplicate_ids_granularity_is_a_parameter(digits, n_kept):
    """Coarser digits collapse more: the threshold is corpus policy, not baked into identity."""
    # --- arrange ----------------------
    ids = [
        FunctionId(101, (ParamValue.decimal(1.0),)),
        FunctionId(101, (ParamValue.decimal(1.0 + 1e-9),)),  # survives the canonical snap, differs at digit 10
    ]

    # --- act / assert -----------------
    assert len(deduplicate_ids(ids, digits=digits)) == n_kept


def test_deduplicate_ids_keeps_distinct_functions():
    """Different parameters, and identical parameters under a different formula, are all separate."""
    # --- arrange ----------------------
    ids = [
        FunctionId(101, (ParamValue.decimal(0.2),)),
        FunctionId(101, (ParamValue.decimal(0.4),)),
        FunctionId(102, (ParamValue.decimal(0.2),)),
    ]

    # --- act / assert -----------------
    assert deduplicate_ids(ids) == tuple(ids)
