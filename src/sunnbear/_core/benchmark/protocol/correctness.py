"""`is_solution_correct` judges whether a solver's answer lies within `xtol` of a root, by finding a proof.

A proof is an x-value in `[x_found - xtol, x_found + xtol]` where the function is exactly zero, or 2
x-values there where it has opposite signs: either way, a root lies within `xtol` of `x_found`. No proof within
`CORRECTNESS_CHECK_MAX_FEVALS` evaluations means the answer is judged incorrect.
"""

import itertools
import math
from collections.abc import Callable, Iterator, Sequence

import numpy as np

from sunnbear._core.utils.floats import FLOAT64_EPS

# The largest number of function evaluations that 1 check spends before it judges the answer incorrect.
CORRECTNESS_CHECK_MAX_FEVALS = 1000


def is_solution_correct(
    *,
    f: Callable[[float], float],
    x_found: float,
    xtol: float,
    seed: int,
    x_candidates: Sequence[float] = (),
) -> bool:
    """Return whether a proof exists that a root of `f` lies within `xtol` of `x_found`.

    A proof is an x-value within `xtol` of `x_found` where `f` is exactly zero, or 2 such x-values where `f`
    has opposite signs. The x-values are probed in this order, stopping at the first proof:

    1. `x_found`, `x_found - xtol` and `x_found + xtol`;
    2. the `x_candidates` within `xtol` of `x_found`, for example the x-values at which the solver
       evaluated `f`: for a bracketing solve, they include the bounds of its final interval, where `f` has
       opposite signs, so they prove that solve's answer correct;
    3. random x-values drawn from `seed`, alternately below and above `x_found`.

    A correct answer of a bracketing solve is usually proven in 2 or 3 evaluations; a wrong answer spends the
    check's whole limit of 1000 evaluations. An x-value where `f` raises or returns a non-finite value proves
    nothing, but counts toward that limit.

    Args:
        f: The plain function, not the wrapper that counts the solver's evaluations, so that the check's
            own evaluations are not counted as the solver's.
        x_found: The solver's answer.
        xtol: The largest distance from `x_found` at which a root still makes the answer correct.
        seed: The seed of the random x-values, so that the verdict is reproducible; any integer.
        x_candidates: X-values to probe before the random x-values, such as the x-values at which the
            solver evaluated `f` (`SolveResult.evaluated_x_values`); x-values farther than `xtol` from `x_found` are
            skipped.

    Raises:
        ValueError: If `xtol` is not positive and finite.
    """
    if not 0.0 < xtol < math.inf:
        raise ValueError(f"xtol must be positive and finite (got {xtol}).")

    # --- the x-values to probe, in order --------
    x_probes = itertools.chain(
        (x_found, x_found - xtol, x_found + xtol),
        (x for x in x_candidates if abs(x - x_found) <= xtol),
        _random_x_probes(x_found, xtol, seed),
    )

    # --- evaluate until a proof is found --------
    has_negative, has_positive = False, False
    for x in itertools.islice(x_probes, CORRECTNESS_CHECK_MAX_FEVALS):
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
def _random_x_probes(x_found: float, xtol: float, seed: int) -> Iterator[float]:
    """Yield random x-values within `xtol` of `x_found` without end, alternately below and above it.

    The x-values come in pairs, 1 below and 1 above `x_found`. The pairs alternate between 2 kinds of distance
    from `x_found`: log-uniform, which clusters the x-values near `x_found`, where a sign change is most
    likely, and uniform.
    """
    rng = np.random.default_rng(seed)
    # Adding a distance below 1 ulp (unit in the last place) of `x_found` returns `x_found` unchanged. When
    # `x_found` is 0, 1 ulp is about 5e-324, so log-uniform distances would spread over hundreds of orders of
    # magnitude and almost all be negligible; the smallest log-uniform distance is therefore also held at or
    # above `xtol · FLOAT64_EPS`.
    log_distance_min = math.log(min(xtol, max(math.ulp(x_found), xtol * FLOAT64_EPS)))
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
