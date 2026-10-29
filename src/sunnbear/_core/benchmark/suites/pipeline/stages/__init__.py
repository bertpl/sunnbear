"""This package holds the stages of the benchmark suite pipeline, 1 module or subpackage per stage.

The name of each stage's module or subpackage starts with ``s`` and its stage's position in the run order, as the
stage's `PipelineStage.output_name` does, so the names sort in run order.
"""

from .s1_candidate_generation import CANDIDATES_SCHEMA, CandidateGenerationStage
from .s2_candidate_validation import C_RANGE_SCHEMA, MAX_BOUND_TO_WIDTH_RATIO, CandidateValidationStage
