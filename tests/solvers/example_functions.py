"""The example functions that the solver tests share, with their roots."""


def cubic(x: float) -> float:
    """Return ``x^3 - x - 1``; it has 1 real root, near 1.3247, and is convex on ``[1, 2]``."""
    return x**3 - x - 1.0


def decreasing_cubic(x: float) -> float:
    """Return the negated `cubic`, so the same root with the decreasing interval orientation."""
    return -cubic(x)


def quintic(x: float) -> float:
    """Return ``x^5 - 2x + 0.5``; it has 1 root in ``[0, 1]``."""
    return x**5 - 2.0 * x + 0.5


CUBIC_ROOT = 1.324717957244746
