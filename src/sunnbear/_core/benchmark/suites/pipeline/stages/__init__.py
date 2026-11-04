"""This package holds the stages of the benchmark suite pipeline, 1 module or subpackage per stage.

The name of each stage's module or subpackage is its stage's `PipelineStageId`, so the names sort in run order. The
subpackage `characterization` holds the base class and the worker task that the 2 characterization stages share.
"""

from .characterization import CandidateCharacterizationStage
from .s1_candidate_generation import CandidateGenerationStage
from .s2_candidate_validation import MAX_BOUND_TO_WIDTH_RATIO, CandidateValidationStage
from .s3_coarse_characterization import CoarseCharacterizationStage
from .s4_spacing import DEFAULT_SPACING_MIN_DISTANCE, SpacingStage
from .s5_full_characterization import FullCharacterizationStage
from .s6_core_selection import CoreSelectionStage
from .s7_distillation import SMALLEST_SUITE_SIZE, DistillationStage
