"""`chord_zero` and `midpoint` compute the chord's zero and the midpoint, the 2 formulas that most solvers share.

Forms of these formulas that are equal in exact arithmetic round differently, which would show as tiny differences
between solvers. So every plain chord step and every plain midpoint of the shipped solvers calls these functions;
section IV.b of ``SOLVER_IMPLEMENTATIONS.md`` lists the steps that keep their source's form.
"""


def chord_zero(a: float, fa: float, b: float, fb: float) -> float:
    """Return the zero of the chord through ``(a, fa)`` and ``(b, fb)``, as ``(a*fb - b*fa) / (fb - fa)``.

    The 2 points may come in either order: swapping them negates the numerator and the denominator, which is exact,
    so the result is the same. ``fa`` and ``fb`` must differ.

    The result is not clamped: where ``(a, fa)`` and ``(b, fb)`` are the interval bounds, rounding can put it on a
    bound or just outside the interval, and a solver clamps it only where its source does.
    """
    return (a * fb - b * fa) / (fb - fa)


def midpoint(a: float, b: float) -> float:
    """Return the midpoint of ``a`` and ``b``, as ``0.5*(a + b)``."""
    return 0.5 * (a + b)
