"""Candidate validation, the second stage of the benchmark suite pipeline, keeps the candidates that pass every check.

The checks run in sequence, cheapest first, and a candidate is rejected by its first failed check:

1. the bound-to-width ratio check, in `bound_to_width_ratio_check`, which rejects an interval that lies far from 0;
2. c-range calibration, in `c_range_calibration`, which finds the range within which the benchmark samples ``c``, and
   rejects a candidate for which it finds none.

`CandidateValidationStage` runs the checks. Its output holds the valid candidates with their c-ranges; its reports
hold the rejected candidates, each with its `RejectionReason`, and the counts of the rejections per formula.
"""

from .bound_to_width_ratio_check import MAX_BOUND_TO_WIDTH_RATIO
from .c_range_calibration import calibrate_c_range
from .rejection_reason import RejectionReason
from .stage import (
    C_RANGE_SCHEMA,
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    CandidateValidationStage,
)
