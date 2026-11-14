"""`CoarseCharacterizationStage`, the third stage of the benchmark suite pipeline, computes the coarse features."""

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.state import CoarseCharacterizationStateAccessor

from .characterization import CandidateCharacterizationStage


# ==================================================================================================
#  CoarseCharacterizationStage
# ==================================================================================================
class CoarseCharacterizationStage(CandidateCharacterizationStage[CoarseCharacterizationStateAccessor]):
    """`CoarseCharacterizationStage` computes each valid candidate's coarse features.

    The coarse features only need to tell the near-duplicate candidates of a formula apart, so the stage runs on every
    valid candidate, by default at `FeatureFidelity.COARSE`, which costs far less per candidate than
    `FeatureFidelity.FULL`.
    """

    stage_id = PipelineStageId.COARSE_CHARACTERIZATION
    default_fidelity = FeatureFidelity.COARSE
