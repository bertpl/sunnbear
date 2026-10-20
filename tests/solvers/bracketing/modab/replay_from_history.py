"""This module replays the interval of a `ModAB` or `ModABSafeguarded` solve from its history."""

from sunnbear.solvers import Interval, ModAB, ModABSafeguarded


def bisection_iterations(
    history: tuple[tuple[float, float], ...], solver_cls: type[ModAB] | type[ModABSafeguarded]
) -> list[int]:
    """Return the 1-based numbers of the iterations whose x-value is the midpoint of the interval, in the form that
    ``solver_cls`` computes: ``0.5*(x1 + x2)`` for `ModAB` and ``0.5*x1 + 0.5*x2`` for `ModABSafeguarded`.

    The interval is replayed from ``history``: each evaluated x-value replaces the bound whose function value has the
    same sign as the function value at that x-value. The replay holds only for a solve that evaluates a new x-value in
    every iteration.
    """
    (a, fa), (b, fb), *evaluations = history
    interval = Interval.from_interval_bounds(a, b, fa, fb)
    iterations = []
    for iteration, (x, fx) in enumerate(evaluations, start=1):
        if solver_cls is ModAB:
            midpoint = 0.5 * (interval.a + interval.b)
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
