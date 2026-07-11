import pytest

from sunnbear.functions import FunctionId, format_param, parse_param


# ==================================================================================================
#  format_param / parse_param
# ==================================================================================================
@pytest.mark.parametrize(
    "value, expected",
    [
        (0.2, "0.2"),
        (1.0, "1.0"),
        (-0.4, "-0.4"),
        (2**1.2, "2^1.2"),
        (10**-3.4, "10^-3.4"),
        (2**12.3, "2^12.3"),
        (4.0, "4.0"),  # ties prefer plain decimal over 2^2.0 / shortest wins
    ],
)
def test_format_param(value, expected):
    assert format_param(value) == expected


@pytest.mark.parametrize("value", [0.2, 1.0, -0.4, 2**1.2, 10**-3.4, 6553.6, 0.0, -17.25])
def test_format_parse_roundtrip_is_exact(value):
    assert parse_param(format_param(value)) == value


# ==================================================================================================
#  FunctionId
# ==================================================================================================
def test_function_id_canonical_string():
    # --- arrange ----------------------
    fid = FunctionId(formula=105, params=(2**1.2, 0.4))

    # --- act / assert -----------------
    assert str(fid) == "f105-2^1.2_0.4"


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
