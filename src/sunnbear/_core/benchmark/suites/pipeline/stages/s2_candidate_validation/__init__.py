"""Candidate validation, the second stage of the benchmark suite pipeline, keeps the candidates that pass every check.

The checks run in sequence, cheapest first, and a candidate is rejected by its first failed check:

1. the bound-to-width ratio check, in `check1_bound_to_width_ratio`, which rejects an interval that lies far from 0;
2. c-range calibration, in `check2_c_range_calibration`, which finds the range within which the benchmark samples
   ``c``, and rejects a candidate for which it finds none;
3. the bisection count check, in `check3_bisection_count`, which rejects a candidate on which `Bisection` does not
   converge in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple of the benchmark;
4. the snuffled diagnostics check, in `check4_snuffled_diagnostics`, which rejects a candidate on which snuffled's
   analysis, at a sample of the tuples that is denser near the ends of the c-range, finds a problem. It runs most of its
   analyses at `SnuffledAnalysisBudget.LOW` and a few at `SnuffledAnalysisBudget.HIGH`.

`CandidateValidationStage` runs the checks. Its output holds the valid candidates with their c-ranges; its reports
hold the rejected candidates, each with its `RejectionReason`, and the counts of the rejections per formula.
"""

from .check1_bound_to_width_ratio import MAX_BOUND_TO_WIDTH_RATIO
from .check2_c_range_calibration import calibrate_c_range
from .check3_bisection_count import is_bisection_count_exact
from .check4_snuffled_diagnostics import find_snuffled_rejection_reason
from .rejection_reason import RejectionReason
from .stage import (
    C_RANGE_SCHEMA,
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    CandidateValidationStage,
)
