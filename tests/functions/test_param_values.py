import pytest

from sunnbear.functions import (
    DecimalParamValue,
    ExponentialParamValue,
    ParamNotation,
    ParamValue,
    deduplicate_param_tuples,
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


@pytest.mark.parametrize(
    "token", ["0.2", "1.0", "-0.4", "2^1.2", "10^-3.4", "6553.6", "0.0", "-17.25", "1e-12", "1e+16", "-1e-12"]
)
def test_param_value_parse_display_roundtrip(token):
    assert ParamValue.parse(token).display() == token


@pytest.mark.parametrize("token", ["0.2", "2^1.2", "10^-3.4", "2^12.3", "1e-12", "-17.25", "1e+16"])
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
    # plain value-object equality; notation-blind collapsing lives in deduplicate_param_tuples
    assert ParamValue.decimal(2.0) != ParamValue.exponential(2, 1.0)
    assert ParamValue.decimal(2.0).value == ParamValue.exponential(2, 1.0).value


@pytest.mark.parametrize(
    "pv, expected_type",
    [
        (ParamValue.decimal(0.2), DecimalParamValue),
        (ParamValue.parse("0.2"), DecimalParamValue),
        (ParamNotation.DECIMAL.build_param_value(0.2), DecimalParamValue),
        (ParamValue.exponential(2, 1.2), ExponentialParamValue),
        (ParamValue.parse("2^1.2"), ExponentialParamValue),
        (ParamNotation.POW2.build_param_value(1.2), ExponentialParamValue),
        (ParamNotation.POW10.build_param_value(1.2), ExponentialParamValue),
    ],
)
def test_factories_build_the_matching_variant(pv, expected_type):
    assert isinstance(pv, expected_type)


@pytest.mark.parametrize(
    "notation, argument, expected",
    [
        (ParamNotation.DECIMAL, 0.4, "0.4"),
        (ParamNotation.POW2, 1.2, "2^1.2"),
        (ParamNotation.POW10, -3.4, "10^-3.4"),
    ],
)
def test_notation_builds_param_value_from_argument(notation, argument, expected):
    """A notation maps a continuous argument to a value; the argument is what the display carries."""
    assert notation.build_param_value(argument).display() == expected


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
    """For a DECIMAL grid the value *is* the argument, so that is what absorbs the float error."""
    assert pv.value == float(f"{pv.value:.12g}")


@pytest.mark.parametrize(
    "pv",
    [
        ExponentialParamValue(value=0.0, base=2, exponent=0.5),  # value is derived, never trusted
        ParamValue.exponential(2, 12.3),
        ParamValue.exponential(10, -3.4000000000000004),
    ],
)
def test_exponential_snaps_its_exponent_and_derives_the_value(pv):
    """For a POW2/POW10 grid the exponent is the argument; the value follows from it untouched."""
    assert pv.exponent == float(f"{pv.exponent:.12g}")
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
#  deduplicate_param_tuples
# ==================================================================================================
def test_dedup_buckets_are_centered_on_round_values():
    """Round numbers are bucket centers, never boundaries: noise on either side of 4.0 collapses onto it."""
    # --- arrange ----------------------
    just_below = (ParamValue.exponential(2, 1.99999999999),)  # value a hair under 4.0
    exact = (ParamValue.decimal(4.0),)
    just_above = (ParamValue.exponential(2, 2.00000000001),)  # value a hair over 4.0

    # --- act / assert -----------------
    assert just_below[0].value < 4.0 < just_above[0].value  # genuinely straddling the round number
    assert len(deduplicate_param_tuples([just_below, exact, just_above])) == 1


def test_deduplicate_collapses_notations_of_one_value():
    # --- arrange ----------------------
    tuples = [
        (ParamValue.decimal(4.0),),
        (ParamValue.exponential(2, 2.0),),
    ]

    # --- act --------------------------
    kept = deduplicate_param_tuples(tuples)

    # --- assert -----------------------
    assert [str(p[0]) for p in kept] == ["4.0"]


def test_deduplicate_collapses_a_near_match():
    """Values differing past the granularity are one function — which exact equality cannot express."""
    # --- arrange ----------------------
    exact = (ParamValue.decimal(4.0),)
    nearly = (ParamValue.exponential(2, 2.00000000001),)  # 2^~2 -> 4.0000000000277

    # --- act / assert -----------------
    assert nearly[0].value != exact[0].value  # genuinely different floats
    assert nearly != exact
    assert len(deduplicate_param_tuples([exact, nearly])) == 1


def test_deduplicate_is_first_come_first_served():
    # --- arrange ----------------------
    as_pow2 = (ParamValue.exponential(2, 2.0),)
    as_decimal = (ParamValue.decimal(4.0),)

    # --- act / assert -----------------
    assert deduplicate_param_tuples([as_pow2, as_decimal]) == (as_pow2,)
    assert deduplicate_param_tuples([as_decimal, as_pow2]) == (as_decimal,)


@pytest.mark.parametrize("digits, n_kept", [(8, 1), (12, 2)])
def test_deduplicate_granularity_is_a_parameter(digits, n_kept):
    """Coarser digits collapse more: the threshold stays a parameter, not baked into equality."""
    # --- arrange ----------------------
    tuples = [
        (ParamValue.decimal(1.0),),
        (ParamValue.decimal(1.0 + 1e-9),),  # survives the canonical snap, differs at digit 10
    ]

    # --- act / assert -----------------
    assert len(deduplicate_param_tuples(tuples, digits=digits)) == n_kept


def test_deduplicate_keeps_distinct_tuples():
    """Different values, and different arities, are all separate."""
    # --- arrange ----------------------
    tuples = [
        (ParamValue.decimal(0.2),),
        (ParamValue.decimal(0.4),),
        (ParamValue.decimal(0.2), ParamValue.decimal(0.4)),
    ]

    # --- act / assert -----------------
    assert deduplicate_param_tuples(tuples) == tuple(tuples)
