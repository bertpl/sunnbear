import pytest

from sunnbear.functions import FunctionId, ParamNotation

# These rendered identities exercise the parser on names, signs, and exponent notation.
_RENDERED_IDS = [
    "f2.1.5[p1=2^1.2,p2=0.4]",
    "f7.1",
    "f2.1.1[p1=0.2]",
    "f2.1.2[p1=5.0]",
    "f2.1.1[p1=-0.4]",  # leading minus in a value
    "f2.1.5[p1=-0.4,p2=-1e-12]",  # negative values and scientific notation on both sides of the comma
    "f2.1.1[p1=1e+16]",  # plus sign inside a value
    "f2.1.1[slope_2=0.5]",  # a name with an underscore and a digit
]


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@pytest.mark.parametrize(
    "fid, expected",
    [
        (FunctionId((2, 1, 5), ("p1", "p2"), (2.0**1.2, 0.4)), "f2.1.5[p1=2^1.2,p2=0.4]"),
        (FunctionId((7, 1), (), ()), "f7.1"),  # no parameters: the number alone, without brackets
    ],
)
def test_function_id_display_includes_each_parameter_name(fid, expected):
    """Each value renders as ``name=value`` in its canonical spelling, in `param_names` order."""
    assert fid.display() == expected


def test_function_id_renders_one_number_alike_however_it_was_authored():
    """``2^2.0`` and ``4.0`` are one float, so their ids are equal and render the same string."""
    # --- arrange ----------------------
    from_decimal = FunctionId((2, 1, 1), ("p1",), (ParamNotation.DECIMAL.build_value_from_argument(4.0),))
    from_pow2 = FunctionId((2, 1, 1), ("p1",), (ParamNotation.POW2.build_value_from_argument(2.0),))

    # --- act / assert -----------------
    assert from_decimal == from_pow2
    assert len({from_decimal, from_pow2}) == 1
    assert str(from_decimal) == str(from_pow2) == repr(from_pow2) == from_pow2.display() == "f2.1.1[p1=4.0]"


def test_function_id_parses_an_authored_spelling_to_the_canonical_id():
    """A non-canonical spelling parses to an equal id, which renders canonically."""
    # --- act --------------------------
    parsed = FunctionId.from_string("f2.1.1[p1=2^2.0]")

    # --- assert -----------------------
    assert parsed == FunctionId.from_string("f2.1.1[p1=4.0]")
    assert str(parsed) == "f2.1.1[p1=4.0]"


def test_function_id_needs_one_name_per_value():
    """A `FunctionId` with more values than names is rejected."""
    with pytest.raises(ValueError, match="1 parameter name"):
        FunctionId((2, 1, 1), ("p1",), (0.2, 0.4))


def test_function_id_equality_is_exact():
    """Floats that differ in the last bits are different ids; collapsing near-matches happens earlier."""
    # --- arrange ----------------------
    exact = FunctionId((2, 1, 1), ("p1",), (4.0,))
    nearly = FunctionId((2, 1, 1), ("p1",), (ParamNotation.POW2.build_value_from_argument(2.00000000001),))

    # --- act / assert -----------------
    assert exact != nearly
    assert len({exact, nearly}) == 2


def test_function_id_with_an_invalid_value_does_not_render():
    """A value that no notation spells with an argument of at most `CANONICAL_DIGITS` digits cannot be rendered."""
    with pytest.raises(ValueError, match="not a valid parameter value"):
        str(FunctionId((2, 1, 1), ("p1",), (0.1 + 0.2,)))


def test_function_id_equality_includes_param_names():
    """Renaming a parameter changes the identity, even when the values are equal."""
    # --- arrange ----------------------
    named_p1 = FunctionId((2, 1, 1), ("p1",), (4.0,))
    named_slope = FunctionId((2, 1, 1), ("slope",), (4.0,))

    # --- act / assert -----------------
    assert named_p1 != named_slope


def test_function_id_equality_with_unrelated_type():
    """A `FunctionId` never equals its rendered string."""
    assert FunctionId((2, 1, 1), ("p1",), (1.0,)) != "f2.1.1[p1=1.0]"


@pytest.mark.parametrize("text", _RENDERED_IDS)
def test_function_id_display_roundtrip(text):
    assert FunctionId.from_string(text).display() == text


@pytest.mark.parametrize("text", _RENDERED_IDS)
def test_function_id_canonical_form_reparses_to_the_same_identity(text):
    original = FunctionId.from_string(text)
    assert FunctionId.from_string(str(original)) == original


def test_function_id_ordering():
    """Ids sort by formula number, then by parameter values."""
    # --- arrange ----------------------
    ids = [
        FunctionId((2, 1, 2), ("p1",), (1.0,)),
        FunctionId((2, 1, 1), ("p1",), (0.4,)),
        FunctionId((2, 1, 1), ("p1",), (0.2,)),
    ]

    # --- act --------------------------
    ordered = sorted(ids)

    # --- assert -----------------------
    assert [str(fid) for fid in ordered] == ["f2.1.1[p1=0.2]", "f2.1.1[p1=0.4]", "f2.1.2[p1=1.0]"]


@pytest.mark.parametrize(
    "text",
    [
        "x2.1.1[p1=0.2]",  # wrong leading letter
        "f[p1=0.2]",  # no number
        "f2.1.1[]",  # empty brackets
        "f2.1.1[p1=zz]",  # value that does not parse
        "f2.1.1[p1=]",  # missing value
        "f2.1.1[=0.2]",  # missing name
        "f2.1.1[p1]",  # no equals sign
        "f2.1.1[1p=0.2]",  # name that is not an identifier
        "f2.1.1[p1=0.2,p1=0.4]",  # repeated name
        "f2.1.1[p1=0.2",  # unclosed bracket
        "f2.1.1[p1=0.2]x",  # trailing text
        "f2.1.1-0.2",  # values after a dash, without names
        "",
    ],
)
def test_function_id_from_string_rejects_invalid(text):
    """Text that does not follow the rendered form raises `ValueError`."""
    with pytest.raises(ValueError):
        FunctionId.from_string(text)
