"""The shared machinery of the twin tests: the cases, the twin's function wrapper, and the agreement check.

A twin is a test-only `Solver` that runs a reference implementation of a solver's algorithm, such as SciPy's or
mpmath's, so that the solver can be compared with it evaluation by evaluation. Every twin test follows the same
rules, so that no twin takes an undocumented approach of its own:

- it runs on `TWIN_CASES`, the cases that all twins share;
- `assert_agrees_with_twin` compares the 2 solves: both converge, and they evaluate the same points, each within
  `MAX_ULPS_APART` of the twin's, until rounding decides the sign of a function value (see that function);
- each difference from exact agreement is declared once, as the `TwinDeviations` of the twin's module, with its
  reason in that module's docstring.

A twin stops where sunnbear's solver would stop, not where the reference implementation would: `TwinFunction`
raises `TwinConverged` once the bracket of the evaluations so far meets `Interval.is_converged`. The 2 solves then
evaluate the same number of points, and their stopping criteria are no declared deviation.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from sunnbear.solvers import Interval, Solver, SolveState, SolveStatus
from tests.solvers.example_functions import cubic, decreasing_cubic, quintic, steep_exponential

# A twin computes the same iterates with its own arithmetic, e.g. a chord's zero anchored at the other bound, so
# its iterates differ from the solver's by a few ulps; 8 leaves room for that while still catching any different
# step, which moves an iterate by far more.
MAX_ULPS_APART = 8

# A budget that no twin case reaches: a solve that hits it ends as MAX_FEVALS, which fails the agreement check.
_MAX_FEVALS = 200


# ==================================================================================================
#  Cases
# ==================================================================================================
@dataclass(frozen=True)
class TwinCase:
    """A `TwinCase` is 1 solve that a solver and its twin both run: a function, its interval, and the tolerance."""

    f: Callable[[float], float]
    a: float
    b: float
    xtol: float

    def __str__(self) -> str:
        """Return a short label for the test id, e.g. ``cubic[1.0,2.0]@1e-10``."""
        return f"{self.f.__name__}[{self.a},{self.b}]@{self.xtol:g}"


TWIN_CASES = [
    TwinCase(f, a, b, xtol)
    for f, a, b in [
        (cubic, 1.0, 2.0),
        (decreasing_cubic, 1.0, 2.0),  # the decreasing orientation
        (quintic, 0.0, 1.0),
        (cubic, 1.3, 4.0),  # a root close to the lower bound
        (steep_exponential, 0.0, 1.0),
    ]
    for xtol in (1e-4, 1e-10)
]


# ==================================================================================================
#  The twin's function
# ==================================================================================================
class TwinConverged(Exception):
    """`TwinConverged` ends a reference implementation's loop once sunnbear's stopping criterion holds.

    Attributes:
        x: The root estimate that sunnbear's solver would report at that point, the bracket's `Interval.root`.
    """

    def __init__(self, x: float) -> None:
        """Hold the root estimate."""
        super().__init__(x)
        self.x = x


class TwinFunction:
    """`TwinFunction` is the function that a twin hands to its reference implementation.

    Each call evaluates through the solve's ``state.f``, so the evaluation is counted, capped and recorded in the
    history. It also splits a plain-float copy of the bracket at the evaluated point, and raises `TwinConverged`
    once that bracket meets `Interval.is_converged`. The copy holds plain floats, so the twin's bookkeeping adds no
    counted flops.

    A reference implementation that evaluates the interval bounds again, after the framework already did, makes
    `n_reevaluated_bounds` such calls first; they do not split the bracket.
    """

    def __init__(self, state: SolveState, n_reevaluated_bounds: int) -> None:
        """Start from the solve's initial interval."""
        interval = state.interval
        self._f = state.f
        self._interval = Interval.from_interval_bounds(
            float(interval.a), float(interval.b), float(interval.fa), float(interval.fb)
        )
        self._doubled_xtol = 2.0 * float(state.xtol)
        self._n_reevaluations_left = n_reevaluated_bounds

    def __call__(self, x: float) -> float:
        """Return ``f(x)``, or raise `TwinConverged` if the bracket that ``f(x)`` leaves meets the stopping criterion."""
        fx = float(self._f(x))
        if self._n_reevaluations_left > 0:
            self._n_reevaluations_left -= 1
        else:
            self._interval = self._interval.split_at(x, fx)
            if self._interval.is_converged(self._doubled_xtol):
                raise TwinConverged(self._interval.root())
        return fx


# ==================================================================================================
#  Agreement
# ==================================================================================================
@dataclass(frozen=True)
class TwinDeviations:
    """`TwinDeviations` declares how a twin differs from exact agreement; the defaults declare none.

    Attributes:
        n_reevaluated_bounds: The number of evaluations that the reference implementation makes at the interval
            bounds before its first iterate, after the framework already evaluated them. The agreement check
            leaves them out of the twin's evaluations.
    """

    n_reevaluated_bounds: int = 0


def assert_agrees_with_twin(solver: Solver, twin: Solver, deviations: TwinDeviations, case: TwinCase) -> None:
    """Assert that `solver` and `twin` both converge on `case`, through the same evaluated points.

    The check walks the 2 lists of evaluated points in step, with the twin's re-evaluations of the interval bounds,
    which `deviations` declares, left out:

    - each pair of points must lie within `MAX_ULPS_APART`, measured by `ulps_apart` against the case's bounds;
    - a pair whose function values differ in sign ends the walk: points that close together straddle the root, so
      rounding decided that sign, and the 2 solves may continue differently. Both still converge, so their root
      estimates lie within ``2 * xtol`` of each other;
    - without such a pair, the 2 solves evaluate equally many points, and their root estimates lie within
      `MAX_ULPS_APART`.
    """
    # --- arrange / act ----------------
    ours = solver.solve(case.f, case.a, case.b, xtol=case.xtol, max_fevals=_MAX_FEVALS, history_enabled=True)
    theirs = twin.solve(case.f, case.a, case.b, xtol=case.xtol, max_fevals=_MAX_FEVALS, history_enabled=True)

    # --- assert -----------------------
    assert ours.status is theirs.status is SolveStatus.CONVERGED
    their_history = list(theirs.history)
    del their_history[2 : 2 + deviations.n_reevaluated_bounds]  # The re-evaluations follow the framework's 2.
    scale = max(abs(case.a), abs(case.b))
    for (our_x, our_fx), (their_x, their_fx) in zip(ours.history, their_history, strict=False):
        assert ulps_apart(our_x, their_x, scale) <= MAX_ULPS_APART, f"{our_x!r} and {their_x!r} differ by more"
        if (our_fx < 0.0) != (their_fx < 0.0):
            assert abs(ours.x - theirs.x) <= 2.0 * case.xtol
            return
    assert len(ours.history) == len(their_history)
    assert ulps_apart(ours.x, theirs.x, scale) <= MAX_ULPS_APART


def ulps_apart(x: float, y: float, scale: float) -> float:
    """Return how far apart ``x`` and ``y`` lie, in units of the float64 spacing at the larger of ``|x|``, ``|y|``
    and ``scale``.

    An iterate is computed from the interval bounds, so its rounding error grows with their magnitude, not with its
    own: an iterate close to 0 in an interval of width 1 carries rounding errors of the size of an ulp of 1. The
    caller passes the bounds' magnitude as ``scale``.
    """
    return abs(x - y) / float(np.spacing(max(abs(x), abs(y), scale)))
