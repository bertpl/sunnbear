"""The constants of `floats` have the values stated in their comments."""

from sunnbear._core.utils.floats import FLOAT64_EPS, FLOAT64_MIN, TINY_LINEAR_TERM_SLOPE


def test_float64_constants_have_stated_values():
    """`FLOAT64_EPS`, `FLOAT64_MIN` and `TINY_LINEAR_TERM_SLOPE` are 2^-52, 2^-1022 and 2^-918."""
    # --- assert -----------------------
    assert (FLOAT64_EPS, FLOAT64_MIN, TINY_LINEAR_TERM_SLOPE) == (2.0**-52, 2.0**-1022, 2.0**-918)
