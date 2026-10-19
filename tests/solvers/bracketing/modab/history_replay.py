"""This module replays the interval of a `ModAB` solve from its history."""

from sunnbear.solvers import Interval, ModABVariant


def bisection_iterations(history: tuple[tuple[float, float], ...], variant: ModABVariant) -> list[int]:
    """Return the 1-based numbers of the iterations whose x-value is the midpoint of the interval, in the form that
    ``variant`` computes: ``(x1 + x2) / 2`` for ``"algorithms_2026"`` and ``0.5*x1 + 0.5*x2`` for
    ``"safeguarded_2026"``.

    The interval is replayed from ``history``: each evaluated x-value replaces the bound whose function value has the
    same sign as the function value at that x-value. The replay holds only for a solve that evaluates a new x-value in
    every iteration.
    """
    (a, fa), (b, fb), *evaluations = history
    interval = Interval.from_interval_bounds(a, b, fa, fb)
    iterations = []
    for iteration, (x, fx) in enumerate(evaluations, start=1):
        if variant is ModABVariant.ALGORITHMS_2026:
            midpoint = (interval.a + interval.b) / 2.0
        else:
            midpoint = 0.5 * interval.a + 0.5 * interval.b
        if x == midpoint:
            iterations.append(iteration)
        interval = interval.split_at(x, fx)
    return iterations


def final_interval(history: tuple[tuple[float, float], ...]) -> Interval:
    """Return the interval that remains after splitting the initial interval at each later x-value of ``history``.

    An iteration that evaluates nothing reuses the function value at a bound, and leaves the interval as it is, so the
    replay holds for every solve.
    """
    (a, fa), (b, fb), *evaluations = history
    interval = Interval.from_interval_bounds(a, b, fa, fb)
    for x, fx in evaluations:
        interval = interval.split_at(x, fx)
    return interval
