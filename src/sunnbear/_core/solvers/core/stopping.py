"""`interval_root_if_converged` applies the shared stopping criterion to 2 interval bounds in either order.

The function holds the criterion of `Interval.is_converged` and the root estimate of `Interval.root`, for the solvers
whose loop keeps the interval bounds in variables of its own, not in an `Interval`.

`Interval` keeps its own methods, because they read its cached width and its cached checks of whether ``fa`` and ``fb``
are 0, which a `BracketingSolver` reuses within an iteration.
"""

from .formulas import midpoint


def interval_root_if_converged(x1: float, f1: float, x2: float, f2: float, xtol_doubled: float) -> float | None:
    """Return the root estimate of `Interval.root` if the criterion of `Interval.is_converged` holds, else ``None``.

    The criterion holds once the interval between ``x1`` and ``x2`` is at most ``xtol_doubled`` wide, or ``f1`` or
    ``f2`` is 0. The root estimate is then a bound with a zero value, or else the midpoint of ``x1`` and ``x2``.

    ``x1`` and ``x2`` may come in either order. ``xtol_doubled`` is ``2*xtol``, which the caller computes once per
    solve, not once per iteration.
    """
    # The criterion is tested before the root estimate is chosen, in the order of `Interval.is_converged` and
    # `Interval.root`, so that the flop counts follow those 2 methods.
    if abs(x2 - x1) <= xtol_doubled or f1 == 0.0 or f2 == 0.0:
        if f1 == 0.0:
            return x1
        elif f2 == 0.0:
            return x2
        else:
            return midpoint(x1, x2)
    else:
        return None
