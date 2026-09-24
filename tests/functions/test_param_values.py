import pytest

from sunnbear.functions import ParamAxis, ParamNotation, deduplicate_param_tuples


# ==================================================================================================
#  ParamNotation.build_value_from_argument
# ==================================================================================================
@pytest.mark.parametrize(
    "notation, argument, expected",
    [
        (ParamNotation.DECIMAL, 0.4, 0.4),
        (ParamNotation.DECIMAL, 1e-12, 1e-12),  # rounding keeps significant digits, so tiny values survive
        (ParamNotation.POW2, 1.2, 2.0**1.2),  # the same float as computing 2 ** 1.2 yourself
        (ParamNotation.POW10, -3.4, 10.0**-3.4),
    ],
)
def test_build_value_from_argument(notation, argument, expected):
    """A notation maps a continuous argument to a value: the argument itself, or a power of the base."""
    assert notation.build_value_from_argument(argument) == expected


@pytest.mark.parametrize(
    "notation, noisy_argument, expected",
    [
        (ParamNotation.DECIMAL, 0.1 + 0.2, 0.3),  # 0.30000000000000004 rounds to the float of 0.3
        (ParamNotation.POW10, -3.4000000000000004, 10.0**-3.4),  # the exponent is rounded, not the value
    ],
)
def test_build_value_rounds_the_argument(notation, noisy_argument, expected):
    """Rounding the argument to `CANONICAL_DIGITS` significant digits removes float error from grid arithmetic."""
    assert notation.build_value_from_argument(noisy_argument) == expected


@pytest.mark.parametrize("notation", list(ParamNotation))
@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_build_value_rejects_non_finite_argument(notation, bad):
    """Every notation rejects a non-finite argument."""
    with pytest.raises(ValueError, match="finite"):
        notation.build_value_from_argument(bad)


def test_build_value_rejects_overflowing_power():
    """A finite exponent can still overflow ``base ** exponent``."""
    with pytest.raises(ValueError, match="non-finite"):
        ParamNotation.POW10.build_value_from_argument(400.0)


# ==================================================================================================
#  ParamNotation.parse_value
# ==================================================================================================
@pytest.mark.parametrize(
    "token, expected",
    [
        ("0.2", 0.2),
        ("-17.25", -17.25),
        ("0.0", 0.0),
        ("1e-12", 1e-12),
        ("1e+16", 1e16),
        ("2^1.2", 2.0**1.2),
        ("10^-3.4", 10.0**-3.4),
        ("0.30000000000000004", 0.3),  # the argument is rounded, as build_value_from_argument rounds it
        ("2^2.0", 4.0),  # the same float as "4.0", so the same value
    ],
)
def test_parse_value(token, expected):
    """A decimal or power spelling parses to its value."""
    assert ParamNotation.parse_value(token) == expected


@pytest.mark.parametrize(
    "token, match",
    [
        ("3^1.4", "Unsupported exponent base"),
        ("2^abc", "Malformed parameter token"),
        ("zz", "Malformed parameter token"),
        ("inf", "finite"),
        ("2^inf", "finite"),
        ("10^nan", "finite"),
    ],
)
def test_parse_value_rejects_bad_tokens(token, match):
    with pytest.raises(ValueError, match=match):
        ParamNotation.parse_value(token)


# ==================================================================================================
#  ParamNotation.spell_value_canonically / is_valid_value
# ==================================================================================================
@pytest.mark.parametrize(
    "value, expected",
    [
        (2.0**2.0, "4.0"),  # authored as 2^2.0: the decimal is shorter
        (2.0**1.23, "2^1.23"),
        (10.0**-5.0, "1e-05"),
        (2.0**10.0, "1024.0"),  # tie in length: the decimal wins
        (1.0, "1.0"),
        (2.0**-20.0, "2^-20.0"),
        (10.0**0.5, "10^0.5"),
        (0.3, "0.3"),
        (-4.0, "-4.0"),  # negative: only the decimal can spell it
        (-0.0, "0.0"),
    ],
)
def test_spell_value_canonically_picks_the_shortest_valid_spelling(value, expected):
    """A valid value renders in its shortest spelling, and a tie in length goes to the decimal."""
    assert ParamNotation.spell_value_canonically(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        0.1 + 0.2,  # 0.30000000000000004 needs 17 decimal digits, and no short exponent reproduces it
        2.0**1.2345678901234,  # its exponent needs 14 digits
        float("inf"),
        float("nan"),
    ],
)
def test_invalid_param_value_is_rejected(value):
    """A value that no notation spells with an argument of at most `CANONICAL_DIGITS` digits is invalid."""
    # --- act / assert -----------------
    assert not ParamNotation.is_valid_value(value)
    with pytest.raises(ValueError, match="not a valid parameter value"):
        ParamNotation.spell_value_canonically(value)


@pytest.mark.parametrize(
    "notation, start, stop, step",
    [
        (ParamNotation.DECIMAL, -5.0, 5.0, 0.1),
        (ParamNotation.POW2, -20.0, 20.0, 0.1),
        (ParamNotation.POW10, -5.0, 5.0, 0.01),
    ],
)
def test_every_built_value_parses_back_from_its_canonical_spelling(notation, start, stop, step):
    """Every value that a `ParamAxis` builds is valid, and parsing its canonical spelling gives the same float."""
    # --- arrange ----------------------
    values = list(ParamAxis("p1", start, stop, step, notation).values())

    # --- act --------------------------
    canonical_spellings = [ParamNotation.spell_value_canonically(value) for value in values]

    # --- assert -----------------------
    assert [ParamNotation.parse_value(token) for token in canonical_spellings] == values


# ==================================================================================================
#  deduplicate_param_tuples
# ==================================================================================================
def test_dedup_buckets_are_centered_on_round_values():
    """Round numbers are bucket centers, never boundaries: noise on either side of 4.0 collapses onto it."""
    # --- arrange ----------------------
    just_below = (ParamNotation.POW2.build_value_from_argument(1.99999999999),)  # slightly under 4.0
    exact = (4.0,)
    just_above = (ParamNotation.POW2.build_value_from_argument(2.00000000001),)  # slightly over 4.0

    # --- act / assert -----------------
    assert just_below[0] < 4.0 < just_above[0]  # genuinely straddling the round number
    assert len(deduplicate_param_tuples([just_below, exact, just_above])) == 1


def test_deduplicate_collapses_a_near_match():
    """Values that differ only beyond `DEDUP_DIGITS` significant digits collapse, though they are unequal floats."""
    # --- arrange ----------------------
    exact = (4.0,)
    nearly = (ParamNotation.POW2.build_value_from_argument(2.00000000001),)  # 2^~2 -> 4.0000000000277

    # --- act / assert -----------------
    assert nearly != exact  # genuinely different floats
    assert len(deduplicate_param_tuples([exact, nearly])) == 1


def test_deduplicate_keeps_the_first_of_each_group():
    """Which near-duplicate survives follows the input order: the first one is kept."""
    # --- arrange ----------------------
    exact = (4.0,)
    nearly = (ParamNotation.POW2.build_value_from_argument(2.00000000001),)

    # --- act / assert -----------------
    assert deduplicate_param_tuples([nearly, exact]) == (nearly,)
    assert deduplicate_param_tuples([exact, nearly]) == (exact,)


@pytest.mark.parametrize("digits, n_kept", [(8, 1), (12, 2)])
def test_deduplicate_granularity_is_a_parameter(digits, n_kept):
    """Coarser digits collapse more: the threshold stays a parameter, not baked into equality."""
    # --- arrange ----------------------
    tuples = [(1.0,), (1.0 + 1e-9,)]  # the second differs at the 10th significant digit

    # --- act / assert -----------------
    assert len(deduplicate_param_tuples(tuples, digits=digits)) == n_kept


def test_deduplicate_keeps_distinct_tuples():
    """Different values, and different arities, are all separate."""
    # --- arrange ----------------------
    tuples = [(0.2,), (0.4,), (0.2, 0.4)]

    # --- act / assert -----------------
    assert deduplicate_param_tuples(tuples) == tuple(tuples)
