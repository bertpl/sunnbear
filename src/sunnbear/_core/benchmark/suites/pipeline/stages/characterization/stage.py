"""`CandidateCharacterizationStage` is the base class of the stages that characterize the candidates."""

from typing import ClassVar

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    DiversityFeatureFactory,
    FeatureFidelity,
    FeatureMatrix,
)
from sunnbear._core.benchmark.suites.pipeline.state import CharacterizationResults, CharacterizationStateAccessor
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

from .task import CandidateCharacterizationResult, CandidateCharacterizationTask


# ==================================================================================================
#  CandidateCharacterizationStage
# ==================================================================================================
class CandidateCharacterizationStage[StateAccessorT: CharacterizationStateAccessor](PipelineStage[StateAccessorT]):
    """`CandidateCharacterizationStage` computes the candidates' raw features, and rejects those whose solves fail.

    The stage stores, as `CharacterizationResults`, for the candidates that it keeps:

    - their raw features;
    - the scale of each feature block, fitted on the kept candidates;
    - their incorrect solves per core solver config.

    An incorrect solve counts as `max_fevals` in `n_fevals_eff`, from which the solvers block is computed. The counts of
    incorrect solves therefore show how much each config's incorrect solves affect the features; the counts never
    reject a candidate.

    A candidate is rejected when 1 of its solves ends with `SolveStatus.FUNCTION_ERROR`, or when snuffled's diagnostics
    reject it at 1 of its analyses, by the rules of `extract_properties_or_rejection_reason`.

    A child class is 1 stage of the pipeline: it sets `stage_id` and `default_fidelity`.

    Class attributes:
        default_fidelity: The `FeatureFidelity` of the stage when the constructor receives none.
    """

    default_fidelity: ClassVar[FeatureFidelity]

    def __init__(self, fidelity: FeatureFidelity | None = None) -> None:
        """Create the stage, which solves each candidate with `DiversityFeatureFactory.solver_ids` at `fidelity`.

        `fidelity` sets only how much work goes into each candidate's features, never which features the stage computes.
        ``None`` stands for the class's `default_fidelity`.
        """
        self.fidelity = fidelity if fidelity is not None else self.default_fidelity

    @property
    def parameters(self) -> dict[str, str]:
        """Return the name of the stage's fidelity."""
        return {"fidelity": self.fidelity.name}

    def run(self, state_accessor: StateAccessorT, *, worker_pool: WorkerPool) -> None:
        """Characterize the candidates, reject those whose solves or analyses fail, and store the results.

        The candidates are characterized in `CandidateCharacterizationTask` tasks on `worker_pool`.
        """
        self._characterize(state_accessor, worker_pool=worker_pool)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _characterize(
        self, state_accessor: StateAccessorT, *, worker_pool: WorkerPool
    ) -> dict[ProblemId, CandidateCharacterizationResult]:
        """Characterize the candidates as `run` describes it, and return the result of each kept candidate."""
        # --- characterize, in the worker pool ---
        c_ranges = state_accessor.c_ranges()
        results_by_problem_id = self._run_in_formula_batches(
            list(c_ranges.items()),
            problem_id_key=lambda candidate: candidate[0],
            build_task=lambda batch: CandidateCharacterizationTask(candidates=batch, fidelity=self.fidelity),
            worker_pool=worker_pool,
        )

        # --- rejections -------------------------
        kept_results: dict[ProblemId, CandidateCharacterizationResult] = {}
        for problem_id in c_ranges:
            result = results_by_problem_id[problem_id]
            if isinstance(result, str):
                state_accessor.reject(problem_id, result)
            else:
                kept_results[problem_id] = result

        # --- results of the kept candidates -----
        raw_feature_matrix = FeatureMatrix(
            problem_ids=tuple(kept_results),
            values=np.array([result.raw_features for result in kept_results.values()]).reshape(
                len(kept_results), len(DiversityFeatureFactory().feature_names)
            ),
        )
        state_accessor.set_characterization_results(
            CharacterizationResults(
                fidelity=self.fidelity,
                raw_feature_matrix=raw_feature_matrix,
                n_incorrect_solves_per_config={
                    problem_id: result.n_incorrect_solves_per_config for problem_id, result in kept_results.items()
                },
            )
        )
        return kept_results
