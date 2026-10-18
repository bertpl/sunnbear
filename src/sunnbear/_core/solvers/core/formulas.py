"""`secant_zero` and `midpoint` compute the secant's zero and the midpoint, the formulas that most solvers share.

Forms of these formulas that are equal in exact arithmetic round differently, which would show as tiny differences
between solvers. So every secant step and every midpoint of the shipped solvers calls these functions, except the steps
that keep their source's form, which the section "Iteration Formula" of ``SOLVER_IMPLEMENTATIONS.md`` lists.
"""


def secant_zero(a: float, fa: float, b: float, fb: float) -> float:
    """Return the zero of the secant through ``(a, fa)`` and ``(b, fb)``, in the form of SciPy's secant method.

    With ``q`` the function value of smaller magnitude divided by the one of larger magnitude, the zero is
    ``(a - q*b) / (1 - q)`` when ``|fb| > |fa|``, else ``(b - q*a) / (1 - q)``. Since ``|q|`` is at most 1, the result
    does not depend on the scale of the function values: it stays finite where the products of the form
    ``(a*fb - b*fa) / (fb - fa)`` would overflow, and keeps its precision where they would underflow.

    The 2 points may come in either order, with the same result. ``fa`` and ``fb`` must differ.

    The result is not clamped: where ``(a, fa)`` and ``(b, fb)`` are the interval bounds, rounding can put it on a
    bound or just outside the interval, and a solver clamps it only where its source does.
    """
    if abs(fb) > abs(fa):
        q = fa / fb
        return (a - q * b) / (1.0 - q)
    else:
        q = fb / fa
        return (b - q * a) / (1.0 - q)


def midpoint(a: float, b: float) -> float:
    """Return the midpoint of ``a`` and ``b``, as ``0.5*(a + b)``."""
    return 0.5 * (a + b)
