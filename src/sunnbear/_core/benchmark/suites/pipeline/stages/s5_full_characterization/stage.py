"""`FullCharacterizationStage` computes the full features and the EDI of each candidate that spacing keeps."""

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.stages.characterization import CandidateCharacterizationStage
from sunnbear._core.benchmark.suites.pipeline.state import FullCharacterizationStateAccessor
from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  FullCharacterizationStage
# ==================================================================================================
class FullCharacterizationStage(CandidateCharacterizationStage[FullCharacterizationStateAccessor]):
    """`FullCharacterizationStage` computes the full features of each candidate that spacing keeps, and its EDI.

    The benchmark suites are selected by the full features, so by default the stage runs at the full fidelity, whose
    tuple sets and snuffled analysis budget are larger than the coarse fidelity's. The stage's block scales are fitted
    only on the candidates that it keeps, because the benchmark suites are selected from those candidates.

    The stage also stores each kept candidate's empirical difficulty index (EDI), computed from the same solves; core
    selection assigns each candidate its difficulty class from its EDI.

    The full fidelity can reject a candidate that the coarse one kept, for example a candidate whose f fails only at an
    x that the coarse fidelity's solves never evaluate, but the solves on the full fidelity's larger tuple set do.
    Spacing does not run again, so the candidates that spacing dropped near such a candidate stay dropped.
    """

    stage_id = PipelineStageId.FULL_CHARACTERIZATION
    default_fidelity = FeatureFidelity.FULL

    def run(self, state_accessor: FullCharacterizationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Characterize the candidates as `CandidateCharacterizationStage.run` does, and store each kept one's EDI."""
        kept_results = self._characterize(state_accessor, worker_pool=worker_pool)
        state_accessor.set_edis({problem_id: result.edi for problem_id, result in kept_results.items()})
