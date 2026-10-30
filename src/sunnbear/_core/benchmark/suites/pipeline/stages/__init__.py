"""This package holds the stages of the benchmark suite pipeline, 1 module or subpackage per stage.

The name of each stage's module or subpackage starts with ``s`` and its stage's position in the run order, as the
stage's `PipelineStage.output_name` does, so the names sort in run order.
"""

from .s1_candidate_generation import CANDIDATES_SCHEMA, CandidateGenerationStage
from .s2_candidate_validation import C_RANGE_SCHEMA, MAX_BOUND_TO_WIDTH_RATIO, CandidateValidationStage
from .s3_coarse_characterization import CoarseCharacterizationStage
from .s4_spacing import (
    CANDIDATE_COUNTS_PER_FORMULA_REPORT_NAME,
    DEFAULT_SPACING_MIN_DISTANCE,
    DROPPED_CANDIDATES_REPORT_NAME,
    NEAREST_KEPT_CANDIDATE_SCHEMA,
    SpacingStage,
)
from .s5_full_characterization import FullCharacterizationStage
from .s6_core_selection import (
    CORE_COMPOSITION_REPORT_NAME,
    DEFAULT_CORE_SELECTION_BUDGET,
    DIFFICULTY_CLASS_SCHEMA,
    CoreComposition,
    CoreCompositionWarning,
    CoreSelectionStage,
    DifficultyClass,
    DifficultyQuota,
)
