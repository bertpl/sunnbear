"""`is_solution_correct` judges whether a solver's answer lies within `xtol` of a root, by finding a proof.

A proof is a point in `[x_found - xtol, x_found + xtol]` where the function is exactly zero, or 2 points
there where it has opposite signs: either way, a root lies within `xtol` of `x_found`. No proof within
`CORRECTNESS_CHECK_MAX_FEVALS` evaluations means the answer is judged incorrect.
"""

import itertools
import math
from collections.abc import Callable, Iterator, Sequence

import numpy as np

# The largest number of function evaluations that 1 check spends before it judges the answer incorrect.
CORRECTNESS_CHECK_MAX_FEVALS = 1000


def is_solution_correct(
    *,
    f: Callable[[float], float],
    x_found: float,
    xtol: float,
    seed: int,
    candidate_points: Sequence[float] = (),
) -> bool:
    """Return whether a proof exists that a root of `f` lies within `xtol` of `x_found`.

    A proof is a point within `xtol` of `x_found` where `f` is exactly zero, or 2 such points where `f`
    has opposite signs. The points are evaluated in this order, stopping at the first proof:

    1. `x_found`, `x_found - xtol` and `x_found + xtol`;
    2. the `candidate_points` within `xtol` of `x_found`, for example the bounds of a bracketing solve's
       final interval: `f` has opposite signs at these bounds, so they prove that solve's answer correct;
    3. random points drawn from `seed`, alternately below and above `x_found`.

    A correct answer of a bracketing solve is usually proven in 2 or 3 evaluations; a wrong answer
    spends all `CORRECTNESS_CHECK_MAX_FEVALS`. A point where `f` raises or returns a non-finite value
    proves nothing, but counts toward `CORRECTNESS_CHECK_MAX_FEVALS`.

    Args:
        f: The plain function, not the wrapper that counts the solver's evaluations, so that the check's
            own evaluations are not counted as the solver's.
        x_found: The solver's answer.
        xtol: The largest distance from `x_found` at which a root still makes the answer correct.
        seed: The seed of the random points, so that the verdict is reproducible; derive it with
            `derive_seed` and `SeedPurpose.CORRECTNESS_CHECK`.
        candidate_points: Points to evaluate before the random points, such as the bounds of a bracketing
            solve's final interval; points farther than `xtol` from `x_found` are skipped.

    Raises:
        ValueError: If `xtol` is not positive and finite.
    """
    if not 0.0 < xtol < math.inf:
        raise ValueError(f"xtol must be positive and finite (got {xtol}).")

    # --- the points, in order of evaluation -----
    points = itertools.chain(
        (x_found, x_found - xtol, x_found + xtol),
        (x for x in candidate_points if abs(x - x_found) <= xtol),
        _random_points(x_found, xtol, seed),
    )

    # --- evaluate until a proof is found --------
    has_negative, has_positive = False, False
    for x in itertools.islice(points, CORRECTNESS_CHECK_MAX_FEVALS):
        fx = _evaluate_or_nan(f, x)
        if fx == 0.0:
            return True
        has_negative = has_negative or fx < 0.0  # NaN compares False, so a failed evaluation proves nothing.
        has_positive = has_positive or fx > 0.0
        if has_negative and has_positive:
            return True
    return False


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _random_points(x_found: float, xtol: float, seed: int) -> Iterator[float]:
    """Yield random points within `xtol` of `x_found` without end, alternately below and above it.

    The points come in pairs, 1 below and 1 above `x_found`. The pairs alternate between 2 kinds of distance
    from `x_found`: log-uniform, which clusters the points near `x_found`, where a sign change is most likely,
    and uniform.
    """
    rng = np.random.default_rng(seed)
    # Adding a distance below 1 ulp (unit in the last place) of `x_found` returns `x_found` unchanged. When
    # `x_found` is 0, 1 ulp is about 5e-324, so log-uniform distances would spread over hundreds of orders of
    # magnitude and almost all be negligible; the smallest log-uniform distance is therefore also held at or
    # above `xtol · 2^-52`, the relative precision of a double.
    log_distance_min = math.log(min(xtol, max(math.ulp(x_found), math.ldexp(xtol, -52))))
    log_distance_max = math.log(xtol)
    while True:
        for is_log_uniform in (True, False):
            for side in (-1.0, 1.0):
                r = rng.random()
                if is_log_uniform:
                    distance = math.exp(log_distance_max + r * (log_distance_min - log_distance_max))
                else:
                    distance = xtol * (1.0 - r)  # The distance lies in (0, xtol], since r lies in [0, 1).
                yield x_found + side * distance


def _evaluate_or_nan(f: Callable[[float], float], x: float) -> float:
    """Return `f(x)`, or NaN when `f` raises or returns a non-finite value."""
    try:
        fx = float(f(x))
    except Exception:  # noqa: BLE001 — a failed evaluation proves nothing, whatever it raised
        return math.nan
    return fx if math.isfinite(fx) else math.nan
