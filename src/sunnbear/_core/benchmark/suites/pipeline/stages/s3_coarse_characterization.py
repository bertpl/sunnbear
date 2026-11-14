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

    The coarse features only need to tell the near-duplicate candidates of a formula apart, so by default the stage
    runs on every valid candidate at the coarse fidelity, which runs fewer solves and fewer snuffled analyses than the
    full fidelity, each analysis at a lower budget.
    """

    stage_id = PipelineStageId.COARSE_CHARACTERIZATION
    default_fidelity = FeatureFidelity.COARSE
