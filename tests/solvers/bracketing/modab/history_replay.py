"""This module replays the interval of a `ModAB` solve from its history."""

from sunnbear.solvers import ModABVariant


def bisection_iterations(history: tuple[tuple[float, float], ...], variant: ModABVariant) -> list[int]:
    """Return the 1-based numbers of the iterations whose x-value is the midpoint of the interval, in the form that
    ``variant`` computes: ``(x1 + x2) / 2`` for ``"algorithms_2026"`` and ``0.5*x1 + 0.5*x2`` for
    ``"safeguarded_2026"``.

    The interval is replayed from ``history``: each evaluated x-value replaces the bound whose function value has the
    same sign as the function value at that x-value. The replay holds only for a solve whose iterations all evaluate.
    """
    (x1, y1), (x2, _) = history[:2]
    iterations = []
    for iteration, (x, y) in enumerate(history[2:], start=1):
        if variant is ModABVariant.ALGORITHMS_2026:
            midpoint = (x1 + x2) / 2.0
        else:
            midpoint = 0.5 * x1 + 0.5 * x2
        if x == midpoint:
            iterations.append(iteration)
        if (y > 0.0) == (y1 > 0.0):
            x1, y1 = x, y
        else:
            x2 = x
    return iterations
