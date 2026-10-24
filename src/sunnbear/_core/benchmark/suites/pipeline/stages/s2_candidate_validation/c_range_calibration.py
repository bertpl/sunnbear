"""c-range calibration, validation's second check, finds the c-range of a candidate.

A candidate's c-range ``[c_min, c_max]``, with ``c_min < 0 < c_max``, is the range within which the benchmark samples
``c``.

Calibration searches the widest range in which every c-value meets 1 condition: ``f(a, c)`` and ``f(b, c)`` are
finite, and ``min(r_a, r_b) > MIN_ENDPOINT_VALUE_RATIO``, with ``r_a = f(a, c)/f(a, 0)`` and
``r_b = f(b, c)/f(b, 0)``. The condition gives 3 things:

- **Signs:** each endpoint value keeps its sign from ``c = 0``, so ``f(a, c)`` and ``f(b, c)`` have opposite signs,
  and the test function keeps the orientation that it has at ``c = 0``, increasing or decreasing.
- **Margin:** each endpoint value keeps more than the fraction `MIN_ENDPOINT_VALUE_RATIO` of its magnitude at
  ``c = 0``, so the root stays away from both endpoints. The margin also makes the range finite for a formula whose
  endpoint values shrink as ``abs(c)`` grows.
- **Overflow and underflow:** a ratio that overflows or underflows still compares correctly with
  `MIN_ENDPOINT_VALUE_RATIO`, while the product ``f(a, c) * f(b, c)``, the usual sign-change test, can underflow to 0,
  as ``1e-170 * -1e-170`` does.

No search can check every c-value in a range, so the search ends by checking the c-values that the benchmark samples.
`calibrate_c_range` runs these steps, steps 2 to 4 on each side of ``c = 0`` separately:

1. Require ``f(a, 0)`` and ``f(b, 0)`` to be finite, nonzero and of opposite signs, because the ratios divide by them.
2. Probe ``abs(c) = FIRST_PROBE_ABS_C``; the condition must hold there.
3. Double ``abs(c)`` until the condition fails, at most `MAX_DOUBLINGS` times; doubling keeps every probe exactly
   representable.
4. Among the c-values evaluated so far on that side, take the one closest to 0 at which the condition fails, and the
   one just closer to 0, at which it holds; halve the interval between them until its ends differ by less than the
   fraction `MAX_BOUND_REL_GAP` of its end closer to 0. The interval's end at which the condition holds is the bound,
   so the condition holds at every c-value evaluated so far within the range.
5. Map the c-values of the benchmark's tuple set onto the range, and check the condition at each. On each side where
   the condition fails at any of these c-values, return to step 4, which now also uses these c-values; return to
   step 4 at most `MAX_RETURNS_TO_HALVING` times.
6. Require the range to be at least `MIN_C_RANGE_WIDTH` wide: across a narrower range, ``c`` changes the test function
   too little to vary the benchmark's samples.

A candidate is rejected at the first step that fails, with that step's `RejectionReason`.
"""

import math
from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.functions.core import XCFun

from .rejection_reason import RejectionReason

# A c-value meets the condition only if each endpoint value keeps its sign and more than this fraction of its
# magnitude at c = 0.
MIN_ENDPOINT_VALUE_RATIO = 0.1
# The search first probes the c-value of this absolute value on each side of c = 0.
FIRST_PROBE_ABS_C = 2.0**-32
# The search doubles abs(c) at most this many times on each side of c = 0.
MAX_DOUBLINGS = 128
# The halving stops once the bound and the c-value at which the condition fails differ by less than this fraction of
# the bound.
MAX_BOUND_REL_GAP = 0.01
# Step 5 returns to step 4 at most this many times before it rejects the candidate.
MAX_RETURNS_TO_HALVING = 10
# Step 6 rejects a c-range narrower than this.
MIN_C_RANGE_WIDTH = 1e-3


# ==================================================================================================
#  CRange
# ==================================================================================================
@dataclass(frozen=True)
class CRange:
    """A `CRange` is the calibrated c-range ``[c_min, c_max]`` of a candidate, with ``c_min < 0 < c_max``."""

    c_min: float
    c_max: float


# ==================================================================================================
#  calibrate_c_range
# ==================================================================================================
def calibrate_c_range(xc_fun: XCFun, a: float, b: float, *, mc_tuples: MCTuples) -> CRange | RejectionReason:
    """Return the c-range of the candidate ``f(x, c)`` on ``[a, b]``, or the reason that calibration rejects it.

    Args:
        xc_fun: The candidate's ``f(x, c)``. A value of `xc_fun` that is not a float, or an exception that `xc_fun`
            raises, counts as a value that is not finite.
        a: The candidate's lower interval bound.
        b: The candidate's upper interval bound.
        mc_tuples: The tuple set whose c-values step 5 checks: the largest size of the benchmark's tuple set, of which
            every smaller size is a prefix.
    """
    try:
        # --- steps 1 to 4 -----------------------
        condition = _CRangeCondition(xc_fun, a, b)
        side_searches = [_CRangeSideSearch(condition, sign=-1.0), _CRangeSideSearch(condition, sign=1.0)]
        for side_search in side_searches:
            side_search.probe_until_failure()
        bounds = [side_search.halve_to_bound() for side_search in side_searches]

        # --- step 5, with its returns to step 4 -
        n_returns = 0
        while True:
            c_range = CRange(c_min=-bounds[0], c_max=bounds[1])
            c_values = mc_tuples.to_c(c_range.c_min, c_range.c_max)
            failing_side_idxs = [
                idx for idx, side_search in enumerate(side_searches) if not side_search.is_met_at_each(c_values)
            ]
            if not failing_side_idxs:
                break
            if n_returns == MAX_RETURNS_TO_HALVING:
                raise _CalibrationFailedError(RejectionReason.CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES)
            for idx in failing_side_idxs:
                bounds[idx] = side_searches[idx].halve_to_bound()
            n_returns += 1

        # --- step 6 -----------------------------
        if c_range.c_max - c_range.c_min < MIN_C_RANGE_WIDTH:
            raise _CalibrationFailedError(RejectionReason.CALIBRATION_C_RANGE_TOO_NARROW)
        else:
            return c_range
    except _CalibrationFailedError as exc:
        return exc.reason


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _CRangeCondition:
    """`_CRangeCondition` evaluates the condition of calibration at a c-value, relative to the endpoint values at 0."""

    def __init__(self, xc_fun: XCFun, a: float, b: float) -> None:
        """Evaluate the endpoint values at ``c = 0``, which the condition divides by, and check them (step 1).

        Raises:
            _CalibrationFailedError: If ``f(a, 0)`` and ``f(b, 0)`` are not both finite and nonzero, with opposite
                signs.
        """
        self.xc_fun = xc_fun
        self.a = a
        self.b = b
        endpoint_values_at_0 = self._endpoint_values(0.0)
        if endpoint_values_at_0 is None:
            raise _CalibrationFailedError(RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0)
        self.fa_0, self.fb_0 = endpoint_values_at_0
        if not (self.fa_0 < 0.0 < self.fb_0 or self.fb_0 < 0.0 < self.fa_0):
            raise _CalibrationFailedError(RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0)

    def is_met(self, c: float) -> bool:
        """Return whether the condition holds at `c`.

        The condition holds when ``f(a, c)`` and ``f(b, c)`` are finite, and their ratios to their values at ``c = 0``
        exceed `MIN_ENDPOINT_VALUE_RATIO`.
        """
        endpoint_values = self._endpoint_values(c)
        if endpoint_values is None:
            return False
        else:
            fa, fb = endpoint_values
            return min(fa / self.fa_0, fb / self.fb_0) > MIN_ENDPOINT_VALUE_RATIO

    def _endpoint_values(self, c: float) -> tuple[float, float] | None:
        """Return ``f(a, c)`` and ``f(b, c)``, or ``None`` when ``f`` raises or either value is not a finite float.

        Without numba's compilation, a formula can return a complex number where its compiled form returns NaN, e.g.
        for ``x**0.5`` at a negative ``x``; `float` raises for a complex number, so it counts as a value that is not
        finite too.
        """
        try:
            fa, fb = float(self.xc_fun(self.a, c)), float(self.xc_fun(self.b, c))
        except Exception:  # noqa: BLE001 — whatever f raises counts as a value that is not finite
            return None
        if math.isfinite(fa) and math.isfinite(fb):
            return fa, fb
        else:
            return None


class _CRangeSideSearch:
    """`_CRangeSideSearch` searches the bound of the c-range on 1 side of ``c = 0``.

    It identifies each c-value on its side by ``abs(c)``, and keeps whether the condition holds at each c-value that it
    evaluated, for the halving of step 4.
    """

    def __init__(self, condition: _CRangeCondition, *, sign: float) -> None:
        """Create the search on the side of ``c = 0`` whose c-values have the sign of `sign`, ``-1.0`` or ``1.0``."""
        self.condition = condition
        self.sign = sign
        self.is_met_by_abs_c: dict[float, bool] = {}

    def evaluate_and_record(self, abs_c: float) -> bool:
        """Return whether the condition holds at the c-value ``sign*abs_c``, and keep the result."""
        is_met = self.condition.is_met(self.sign * abs_c)
        self.is_met_by_abs_c[abs_c] = is_met
        return is_met

    def probe_until_failure(self) -> None:
        """Probe ``abs(c) = FIRST_PROBE_ABS_C``, then double ``abs(c)`` until the condition fails (steps 2 and 3).

        Raises:
            _CalibrationFailedError: If the condition fails at the first probe, or still holds after the last doubling.
        """
        abs_c = FIRST_PROBE_ABS_C
        if not self.evaluate_and_record(abs_c):
            raise _CalibrationFailedError(RejectionReason.CALIBRATION_FAILS_AT_FIRST_PROBE)
        for _ in range(MAX_DOUBLINGS):
            abs_c *= 2.0
            if not self.evaluate_and_record(abs_c):
                return
        raise _CalibrationFailedError(RejectionReason.CALIBRATION_NO_BOUND_FOUND)

    def is_met_at_each(self, c_values: np.ndarray) -> bool:
        """Return whether the condition holds at each of `c_values` that lies on this side (step 5).

        Every such c-value is evaluated, also after the first failure, so that a return to step 4 finds the failing
        c-value closest to 0.
        """
        is_met_at_c_values = [self.evaluate_and_record(float(c) * self.sign) for c in c_values if c * self.sign > 0.0]
        return all(is_met_at_c_values)

    def halve_to_bound(self) -> float:
        """Return the bound of ``abs(c)`` on this side, from the c-values evaluated so far (step 4).

        The halving starts from the interval between 2 of those c-values: the one closest to 0 at which the condition
        fails, and the one just closer to 0, at which it holds.

        It halves the interval until its ends differ by less than `MAX_BOUND_REL_GAP` times its end closer to 0, and
        returns the end at which the condition holds.

        Raises:
            _CalibrationFailedError: If the condition fails at the evaluated c-value closest to 0. Only a c-value of
                the benchmark's tuple set can lie closer to 0 than the first probe, so the error carries the
                `RejectionReason` of step 5.
        """
        abs_cs = sorted(self.is_met_by_abs_c)
        idx_first_failing = next(idx for idx, abs_c in enumerate(abs_cs) if not self.is_met_by_abs_c[abs_c])
        if idx_first_failing == 0:
            raise _CalibrationFailedError(RejectionReason.CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES)
        abs_c_met, abs_c_failing = abs_cs[idx_first_failing - 1], abs_cs[idx_first_failing]
        while abs_c_failing - abs_c_met >= MAX_BOUND_REL_GAP * abs_c_met:
            abs_c_mid = 0.5 * (abs_c_met + abs_c_failing)
            if self.evaluate_and_record(abs_c_mid):
                abs_c_met = abs_c_mid
            else:
                abs_c_failing = abs_c_mid
        return abs_c_met


class _CalibrationFailedError(Exception):
    """`_CalibrationFailedError` ends the calibration of a candidate at the step that rejects it."""

    def __init__(self, reason: RejectionReason) -> None:
        """Hold the `RejectionReason` of the failing step."""
        super().__init__(reason.value)
        self.reason = reason
