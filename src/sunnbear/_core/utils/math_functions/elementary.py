"""This module holds the sign and the real odd root, which `math` lacks."""

import numba


@numba.njit
def sign(value: float) -> float:
    """Return -1.0, 0.0 or 1.0 for a negative, zero or positive `value`, and NaN for NaN."""
    if value > 0.0:
        return 1.0
    elif value < 0.0:
        return -1.0
    elif value == 0.0:
        return 0.0
    else:
        return value


@numba.njit
def real_root(value: float, n: int) -> float:
    """Return the real `n`-th root of `value`, for an odd `n`: negative for a negative `value`.

    In numba, `value**(1/n)` is NaN for a negative `value`, and in plain Python it is complex. For a value of 0 or more,
    the result is `value**(1/n)` exactly, with the rounding of that power.
    """
    if value < 0.0:
        return -((-value) ** (1.0 / n))
    else:
        return value ** (1.0 / n)
