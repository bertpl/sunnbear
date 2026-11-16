"""`FineCharacterizationStage` computes the fine features and the EDI of each candidate that spacing keeps."""

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.stages.characterization import CandidateCharacterizationStage
from sunnbear._core.benchmark.suites.pipeline.state import FineCharacterizationStateAccessor
from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  FineCharacterizationStage
# ==================================================================================================
class FineCharacterizationStage(CandidateCharacterizationStage[FineCharacterizationStateAccessor]):
    """`FineCharacterizationStage` computes the fine features of each candidate that spacing keeps, and its EDI.

    The benchmark suites are selected by the fine features, so by default the stage runs at
    `FeatureFidelity.FINE_PRODUCTION`, the most expensive fidelity.

    The stage's block scales are fitted only on the candidates that it keeps, because the benchmark suites are selected
    from those candidates.

    The stage also stores each kept candidate's empirical difficulty index (EDI), computed from the same solves.

    At `FeatureFidelity.FINE_PRODUCTION`, the stage can reject a candidate that coarse characterization kept at
    `FeatureFidelity.COARSE_PRODUCTION`, for example a candidate whose f fails only at an x that the solves at
    `FeatureFidelity.COARSE_PRODUCTION` never evaluate, but the solves on the larger tuple set of
    `FeatureFidelity.FINE_PRODUCTION` do. Spacing does not run again, so the candidates that spacing dropped near such a
    candidate stay dropped.
    """

    stage_id = PipelineStageId.FINE_CHARACTERIZATION
    default_fidelity = FeatureFidelity.FINE_PRODUCTION

    def run(self, state_accessor: FineCharacterizationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Characterize the candidates as `CandidateCharacterizationStage.run` does, and store each kept one's EDI."""
        kept_results = self._characterize(state_accessor, worker_pool=worker_pool)
        state_accessor.set_edis({problem_id: result.edi for problem_id, result in kept_results.items()})
