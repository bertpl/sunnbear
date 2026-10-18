"""`secant_zero` and `midpoint` compute the secant's zero and the midpoint, the formulas that most solvers share.

Forms of these formulas that are equal in exact arithmetic round differently, which would show as tiny differences
between solvers. So every secant step and every midpoint of the shipped solvers calls these functions, except the steps
that keep their source's form, which the section "Iteration Formula" of ``SOLVER_IMPLEMENTATIONS.md`` lists.
"""


def secant_zero(a: float, fa: float, b: float, fb: float) -> float:
    """Return the zero of the secant through ``(a, fa)`` and ``(b, fb)``, as ``(a*fb - b*fa) / (fb - fa)``.

    The 2 points may come in either order: swapping them negates the numerator and the denominator, which is exact,
    so the result is the same. ``fa`` and ``fb`` must differ.

    The result is not clamped: where ``(a, fa)`` and ``(b, fb)`` are the interval bounds, rounding can put it on a
    bound or just outside the interval, and a solver clamps it only where its source does.
    """
    return (a * fb - b * fa) / (fb - fa)


def midpoint(a: float, b: float) -> float:
    """Return the midpoint of ``a`` and ``b``, as ``0.5*(a + b)``."""
    return 0.5 * (a + b)
