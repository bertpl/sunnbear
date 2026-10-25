"""`RejectionReason` names why candidate validation rejected a candidate."""

from enum import StrEnum


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the validation check that rejected a candidate, and for calibration the failing step.

    The calibration reasons follow the steps of `calibrate_c_range`.
    """

    BOUND_TO_WIDTH_RATIO = "bound_to_width_ratio"
    # f(a, 0) and f(b, 0) are not both finite and nonzero, with opposite signs.
    CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0 = "calibration_no_finite_sign_change_at_0"
    # The condition fails at the first probe, on either side of c = 0.
    CALIBRATION_FAILS_AT_FIRST_PROBE = "calibration_fails_at_first_probe"
    # The condition still holds after the last doubling of abs(c), on either side of c = 0.
    CALIBRATION_NO_BOUND_FOUND = "calibration_no_bound_found"
    # The condition still fails at 1 of the benchmark's c-values after the last return to step 4 of the search.
    CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES = "calibration_fails_at_benchmark_c_values"
    # The c-range is narrower than `MIN_C_RANGE_WIDTH` at step 6 of the search.
    CALIBRATION_C_RANGE_TOO_NARROW = "calibration_c_range_too_narrow"
    # At 1 of the tuples, `Bisection` does not converge in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations.
    BISECTION_COUNT = "bisection_count"
