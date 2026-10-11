"""This module holds `xtol_for_t`, which lets a test run `Brent` with a published absolute tolerance ``t``."""

from sunnbear._core.utils.floats import FLOAT64_EPS


def xtol_for_t(t: float, a: float, b: float) -> float:
    """Return the ``xtol`` from which `Brent` derives the absolute tolerance ``t`` of Brent's procedure ``zero`` on the
    interval ``[a, b]``, by inverting the formula in the class docstring of `Brent`."""
    return 2.0 * t + 6.0 * FLOAT64_EPS * max(abs(a), abs(b))
