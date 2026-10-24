"""This package holds the stages of the benchmark suite pipeline, 1 module per stage.

Each module's name starts with ``s`` and its stage's position in the run order, as the stage's
`PipelineStage.output_name` does, so the modules sort in run order.
"""

from .s1_candidate_generation import CANDIDATES_SCHEMA, CandidateGenerationStage
from .s2_candidate_validation import (
    MAX_BOUND_TO_WIDTH_RATIO,
    REJECTED_CANDIDATES_SCHEMA,
    CandidateValidationStage,
    RejectionReason,
)
