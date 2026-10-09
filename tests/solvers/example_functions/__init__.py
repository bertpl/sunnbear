"""The example functions that the solver tests share, with their roots."""

import math


def cubic(x: float) -> float:
    """Return ``x^3 - x - 1``; it has 1 real root, near 1.3247, and is convex on ``[1, 2]``."""
    return x**3 - x - 1.0


def decreasing_cubic(x: float) -> float:
    """Return the negated `cubic`, giving the same root under the decreasing interval orientation."""
    return -cubic(x)


def quintic(x: float) -> float:
    """Return ``x^5 - 2x + 0.5``; it has 1 root in ``[0, 1]``."""
    return x**5 - 2.0 * x + 0.5


CUBIC_ROOT = 1.324717957244746


def ninth_power(x: float) -> float:
    """Return ``x^9``; its root at 0 is a multiple root, around which the function is flat."""
    return x**9


def steep_exponential(x: float) -> float:
    """Return ``exp(20x) - 10^4``; it rises steeply and is convex on ``[0, 1]``, with its root at
    `STEEP_EXPONENTIAL_ROOT`."""
    return math.exp(20.0 * x) - 1.0e4


STEEP_EXPONENTIAL_ROOT = math.log(1.0e4) / 20.0
