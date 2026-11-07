"""`CandidateCharacterizationTask` computes the feature vector of each candidate of a batch, or the reason to reject it.

For each candidate, the task first runs the solves of the core solver configs, then snuffled's analyses, in the same
worker, so that each formula is compiled in only 1 worker. Besides the feature vector, the task counts the candidate's
incorrect solves for each core solver config.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.aggregation import add_derived_results
from sunnbear._core.benchmark.mc_tuples import load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings
from sunnbear._core.benchmark.runner import BenchmarkRunSettings, BenchmarkTask
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, RejectionReason
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.solvers.core import SolveStatus
from sunnbear._core.stats import gpq

from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS
from .fevals_mapping import map_fevals_to_feature
from .fidelity import FeatureFidelity


# ==================================================================================================
#  CandidateCharacterizationTask
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class CandidateCharacterizationTask:
    """A `CandidateCharacterizationTask` computes each candidate's `CandidateCharacterizationResult`, or rejects it.

    Attributes:
        candidates: The ``(problem_id, c_min, c_max)`` of each candidate: its id, as rendered by `ProblemId`, and its
            c-range. The task rebuilds each calibrated test problem from them.
        solver_ids: The ids of the core solver configs, whose solves give the solvers block of the feature vector.
        feature_column_names: The names of the feature vector's columns, in its order, as the characterization stage
            names them.
        fidelity: The `FeatureFidelity` of the feature vectors.
    """

    candidates: tuple[tuple[str, float, float], ...]
    solver_ids: tuple[str, ...]
    feature_column_names: tuple[str, ...]
    fidelity: FeatureFidelity

    def run(self) -> list["CandidateCharacterizationResult | RejectionReason"]:
        """Return each candidate's characterization result, or the reason to reject it, in the order of `candidates`."""
        return [self._characterize_candidate(problem_id, c_min, c_max) for problem_id, c_min, c_max in self.candidates]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _characterize_candidate(
        self, problem_id: str, c_min: float, c_max: float
    ) -> "CandidateCharacterizationResult | RejectionReason":
        """Return the candidate's characterization result, or the reason to reject it.

        The solves come first: a solve that ends with `SolveStatus.FUNCTION_ERROR`, where f fails inside the interval,
        rejects the candidate before snuffled runs. snuffled's analyses then run in the order of their tuples, and the
        first one whose diagnostics reject the candidate stops them.
        """
        # --- solvers block ----------------------
        solve_results = BenchmarkTask(
            problem_id=problem_id,
            c_min=c_min,
            c_max=c_max,
            solver_ids=self.solver_ids,
            run_settings=BenchmarkRunSettings(
                mc_size=self.fidelity.solver_mc_size,
                n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
                root_seed=PIPELINE_ROOT_SEED,
            ),
        ).run()
        if (solve_results["status"] == SolveStatus.FUNCTION_ERROR.value).any():
            return RejectionReason.FUNCTION_ERROR
        else:
            # Every solve of a candidate has the same evaluation budget, `max_fevals`, so the first row's value holds
            # for all of them.
            max_fevals = int(solve_results["max_fevals"][0])
            # The rows are ordered sample by sample, and within a sample, solver by solver in the order of `solver_ids`.
            n_fevals_eff = (
                add_derived_results(solve_results)["n_fevals_eff"].to_numpy().reshape(-1, len(self.solver_ids))
            )
            n_incorrect_solves = (~solve_results["is_correct"]).to_numpy().reshape(-1, len(self.solver_ids)).sum(axis=0)
            solvers_fevals_statistics = [
                *np.exp(np.log(n_fevals_eff).mean(axis=0)),
                *(gpq(n_fevals_eff.ravel(), level) for level in SOLVERS_GPQ_LEVELS),
            ]

            # --- snuffled block -----------------
            problem = FormulaRegistry.candidate_from_id(problem_id).calibrated(c_min, c_max)
            mc_solve_settings = MCSolveSettings.from_test_problem(
                problem,
                n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
                mc_tuples=load_mc_tuples(self.fidelity.snuffled_mc_size),
            )
            property_values = []
            for mc_sample_idx in range(self.fidelity.snuffled_mc_size):
                result = self.fidelity.snuffled_budget.extract_properties_or_rejection_reason(
                    problem, SNUFFLED_PROPERTIES, mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx
                )
                if isinstance(result, RejectionReason):
                    return result
                property_values.append(list(result.values()))
            snuffled_features = np.mean(property_values, axis=0)

            # --- feature vector -----------------
            feature_values = [
                *map_fevals_to_feature(solvers_fevals_statistics, max_fevals=max_fevals),
                *snuffled_features,
            ]
            return CandidateCharacterizationResult(
                features=dict(zip(self.feature_column_names, map(float, feature_values), strict=True)),
                n_incorrect_solves_per_config=tuple(int(count) for count in n_incorrect_solves),
            )


# ==================================================================================================
#  CandidateCharacterizationResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class CandidateCharacterizationResult:
    """A `CandidateCharacterizationResult` holds 1 candidate's feature vector, and the counts of its incorrect solves.

    Attributes:
        features: The feature vector, which maps the task's `feature_column_names` to their values.
        n_incorrect_solves_per_config: For each core solver config, in the order of the task's `solver_ids`, the
            number of its solves without a correct answer.
    """

    features: dict[str, float]
    n_incorrect_solves_per_config: tuple[int, ...]
