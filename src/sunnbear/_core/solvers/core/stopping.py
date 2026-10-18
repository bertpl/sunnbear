"""`is_interval_converged` and `interval_root` apply the shared stopping criterion to 2 interval bounds in either order.

They hold the criterion of `Interval.is_converged` and the root estimate of `Interval.root`, for the solvers whose
loop keeps the interval bounds in variables of its own, not in an `Interval`.

`Interval` keeps its own methods, because they read its cached width and its cached checks of whether ``fa`` and ``fb``
are 0, which a `BracketingSolver` reuses within an iteration.
"""


def is_interval_converged(x1: float, f1: float, x2: float, f2: float, xtol_doubled: float) -> bool:
    """Return whether the interval between ``x1`` and ``x2`` is at most ``xtol_doubled`` wide, or ``f1`` or ``f2`` is 0.

    ``x1`` and ``x2`` may come in either order. ``xtol_doubled`` is ``2*xtol``, which the caller computes once per
    solve, not once per iteration.
    """
    return abs(x2 - x1) <= xtol_doubled or f1 == 0.0 or f2 == 0.0


def interval_root(x1: float, f1: float, x2: float, f2: float) -> float:
    """Return the root estimate between ``x1`` and ``x2``: a bound with a zero value, else their midpoint.

    The midpoint takes the form of `Interval.midpoint`, so that every solver returns the same x-value for the same
    interval.
    """
    if f1 == 0.0:
        return x1
    elif f2 == 0.0:
        return x2
    else:
        return 0.5 * (x1 + x2)
