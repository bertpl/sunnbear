import pytest

from sunnbear.functions import FunctionId, ParamValue

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
        (
            FunctionId((2, 1, 5), ("p1", "p2"), (ParamValue.exponential(2, 1.2), ParamValue.decimal(0.4))),
            "f2.1.5[p1=2^1.2,p2=0.4]",
        ),
        (FunctionId((7, 1), (), ()), "f7.1"),  # no parameters: the number alone, without brackets
    ],
)
def test_function_id_display_includes_each_parameter_name(fid, expected):
    """Each value renders as ``name=value`` in its authored notation, in `param_names` order."""
    assert fid.display() == expected


def test_function_id_rendering_is_faithful():
    """One rendering, carrying the authored notation, so a published identity reproduces exactly."""
    # --- arrange ----------------------
    as_decimal = FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId((2, 1, 1), ("p1",), (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert str(as_decimal) == "f2.1.1[p1=4.0]"
    assert str(as_pow2) == "f2.1.1[p1=2^2.0]"  # not flattened to the decimal spelling
    assert repr(as_pow2) == str(as_pow2) == as_pow2.display()


def test_function_id_needs_one_name_per_value():
    """A `FunctionId` with more values than names is rejected."""
    with pytest.raises(ValueError, match="1 parameter name"):
        FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(0.2), ParamValue.decimal(0.4)))


def test_function_id_equality_is_exact():
    """Equality stays a real equivalence over exact values; collapsing near-matches happens earlier."""
    # --- arrange ----------------------
    as_decimal = FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(4.0),))
    as_pow2 = FunctionId((2, 1, 1), ("p1",), (ParamValue.exponential(2, 2.0),))

    # --- act / assert -----------------
    assert as_decimal != as_pow2  # same number, different notation: two identities
    assert len({as_decimal, as_pow2}) == 2
    assert as_decimal == FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(4.0),))  # and reflexive on equal spellings


def test_function_id_equality_includes_param_names():
    """Renaming a parameter changes the identity, even when the values are equal."""
    # --- arrange ----------------------
    named_p1 = FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(4.0),))
    named_slope = FunctionId((2, 1, 1), ("slope",), (ParamValue.decimal(4.0),))

    # --- act / assert -----------------
    assert named_p1 != named_slope


def test_function_id_equality_with_unrelated_type():
    """A `FunctionId` never equals its rendered string."""
    assert FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(1.0),)) != "f2.1.1[p1=1.0]"


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
        FunctionId((2, 1, 2), ("p1",), (ParamValue.decimal(1.0),)),
        FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(0.4),)),
        FunctionId((2, 1, 1), ("p1",), (ParamValue.decimal(0.2),)),
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
