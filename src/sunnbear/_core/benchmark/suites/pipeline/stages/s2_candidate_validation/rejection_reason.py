"""`RejectionReason` names why candidate validation rejected a candidate."""

from enum import StrEnum


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the check that rejected a candidate, or for some checks the condition that failed.

    The calibration reasons follow the steps of `calibrate_c_range`; each snuffled reason names a condition under which
    `find_snuffled_rejection_reason` rejects a candidate, in the order in which it tests the conditions.
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
    BISECTION_COUNT_NOT_EXACT = "bisection_count_not_exact"
    # At 1 of the sampled tuples, f raises during snuffled's analysis.
    SNUFFLED_F_RAISES = "snuffled_f_raises"
    # At 1 of the sampled tuples, snuffled's diagnostic whose name follows `SNUFFLED_` is above 0.
    SNUFFLED_NAN_VALUES_DETECTED = "snuffled_nan_values_detected"
    SNUFFLED_INF_VALUES_DETECTED = "snuffled_inf_values_detected"
    SNUFFLED_NO_ZEROS_DETECTED = "snuffled_no_zeros_detected"
    SNUFFLED_INTERVAL_NOT_BRACKETING_READY = "snuffled_interval_not_bracketing_ready"
    SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE = "snuffled_all_roots_too_close_to_edge"
    # At 1 of the sampled tuples, snuffled's `MAX_ZERO_WIDTH` exceeds `MAX_ZERO_WIDTH_IN_XTOL` times the tuple's `xtol`.
    SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE = "snuffled_max_zero_width_too_large"
