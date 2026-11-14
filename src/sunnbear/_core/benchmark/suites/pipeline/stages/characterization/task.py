"""`CandidateCharacterizationTask` computes the raw features of each candidate of a batch, or the reason to reject it.

For each candidate, the task first runs the solves of the core solver configs that `DiversityFeatureFactory` names,
then snuffled's analyses, in the same worker, so that each formula is compiled in only 1 worker. Besides the raw
features, the task computes the candidate's EDI and counts its incorrect solves for each core solver config.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.aggregation import add_derived_results
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, CRange, MCSolveSettings
from sunnbear._core.benchmark.runner import BenchmarkRunSettings, BenchmarkTask
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED
from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    SNUFFLED_PROPERTIES,
    DiversityFeatureFactory,
    FeatureFidelity,
    compute_edi,
)
from sunnbear._core.problems.core import FormulaRegistry, ProblemId
from sunnbear._core.solvers.core import SolveStatus


# ==================================================================================================
#  CandidateCharacterizationTask
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class CandidateCharacterizationTask:
    """A `CandidateCharacterizationTask` computes each candidate's `CandidateCharacterizationResult`, or rejects it.

    Attributes:
        candidates: The id and the c-range of each candidate; the task rebuilds each calibrated test problem from them.
        fidelity: The `FeatureFidelity` of the solves and analyses.
    """

    candidates: tuple[tuple[ProblemId, CRange], ...]
    fidelity: FeatureFidelity

    def run(self) -> list["CandidateCharacterizationResult | str"]:
        """Return each candidate's characterization result, or the reason to reject it, in the order of `candidates`."""
        return [self._characterize_candidate(problem_id, c_range) for problem_id, c_range in self.candidates]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _characterize_candidate(
        self, problem_id: ProblemId, c_range: CRange
    ) -> "CandidateCharacterizationResult | str":
        """Return the candidate's characterization result, or the reason to reject it.

        The solves come first: a solve that ends with `SolveStatus.FUNCTION_ERROR`, where f fails inside the interval,
        rejects the candidate before snuffled runs. snuffled's analyses then run in the order of their tuples, and the
        first one whose diagnostics reject the candidate stops them.
        """
        # --- solves -----------------------------
        factory = DiversityFeatureFactory()
        solver_ids = factory.solver_ids
        solve_results = BenchmarkTask(
            problem_id=str(problem_id),
            c_min=c_range.c_min,
            c_max=c_range.c_max,
            solver_ids=solver_ids,
            run_settings=BenchmarkRunSettings(
                mc_size=self.fidelity.solver_mc_size,
                n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
                root_seed=PIPELINE_ROOT_SEED,
            ),
        ).run()
        if (solve_results["status"] == SolveStatus.FUNCTION_ERROR.value).any():
            # f raises, or returns a value that is not finite, at an x inside the interval.
            return "function_error"
        else:
            # The rows are ordered sample by sample, and within a sample, solver by solver in the order of `solver_ids`.
            n_fevals_eff = add_derived_results(solve_results)["n_fevals_eff"].to_numpy().reshape(-1, len(solver_ids))
            n_incorrect_solves_per_config = (
                (~solve_results["is_correct"]).to_numpy().reshape(-1, len(solver_ids)).sum(axis=0)
            )

            # --- snuffled's analyses ------------
            problem = FormulaRegistry.candidate_from_id(problem_id).calibrated(c_range.c_min, c_range.c_max)
            mc_solve_settings = MCSolveSettings.from_test_problem(
                problem,
                n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
                mc_tuples=self.fidelity.snuffled_mc_tuples,
            )
            property_values = []
            for mc_sample_idx in range(self.fidelity.n_snuffled_analyses):
                result = self.fidelity.snuffled_budget.extract_properties_or_rejection_reason(
                    problem, SNUFFLED_PROPERTIES, mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx
                )
                if isinstance(result, str):
                    return result
                property_values.append(list(result.values()))

            # --- result -------------------------
            return CandidateCharacterizationResult(
                raw_features=factory.compute_raw_feature_row(
                    n_fevals_eff=n_fevals_eff, snuffled_property_values=np.array(property_values)
                ),
                edi=compute_edi(n_fevals_eff),
                n_incorrect_solves_per_config=tuple(int(count) for count in n_incorrect_solves_per_config),
            )


# ==================================================================================================
#  CandidateCharacterizationResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class CandidateCharacterizationResult:
    """A `CandidateCharacterizationResult` holds 1 candidate's raw features, EDI and counts of incorrect solves.

    Attributes:
        raw_features: The raw features, in the order of `DiversityFeatureFactory.feature_names`.
        edi: The candidate's empirical difficulty index (EDI).
        n_incorrect_solves_per_config: For each core solver config, in the order of
            `DiversityFeatureFactory.solver_ids`, the number of its solves without a correct answer.
    """

    raw_features: np.ndarray
    edi: float
    n_incorrect_solves_per_config: tuple[int, ...]
