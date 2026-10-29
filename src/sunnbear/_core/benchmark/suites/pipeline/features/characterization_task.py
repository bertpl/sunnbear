"""`CandidateCharacterizationTask` computes the feature vector of each candidate of a batch, or the reason to reject it.

For each candidate, the task first runs the solves of the empirical block, then snuffled's analyses of the
analytical block, in the same worker, so that each formula is compiled in only 1 worker. The task runs in a worker
process of the pool, or in the calling process.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.aggregation import add_derived_results
from sunnbear._core.benchmark.mc_tuples import load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings
from sunnbear._core.benchmark.runner import BenchmarkRunSettings, BenchmarkTask
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, RejectionReason
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import extract_properties_or_rejection_reason
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.solvers.core import SolveStatus
from sunnbear._core.stats import gpq

from .fidelity import ANALYTICAL_PROPERTIES, EMPIRICAL_GPQ_LEVELS, FeatureFidelity


# ==================================================================================================
#  CandidateCharacterizationTask
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class CandidateCharacterizationTask:
    """A `CandidateCharacterizationTask` computes the feature vector of each candidate in `candidates`, or rejects it.

    Attributes:
        candidates: The ``(problem_id, c_min, c_max)`` of each candidate: its id, as rendered by `ProblemId`, and its
            c-range. The task rebuilds each calibrated test problem from them.
        solver_ids: The ids of the core solver configs, whose solves form the empirical block.
        fidelity: The fidelity at which the task computes the feature vectors.
    """

    candidates: tuple[tuple[str, float, float], ...]
    solver_ids: tuple[str, ...]
    fidelity: FeatureFidelity

    def run(self) -> list[dict[str, float] | RejectionReason]:
        """Return each candidate's feature vector, or the reason to reject it, in the order of `candidates`.

        A feature vector maps the names of `FeatureFidelity.feature_column_names` to their values.
        """
        return [self._characterize_candidate(problem_id, c_min, c_max) for problem_id, c_min, c_max in self.candidates]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _characterize_candidate(
        self, problem_id: str, c_min: float, c_max: float
    ) -> dict[str, float] | RejectionReason:
        """Return the candidate's feature vector, or the reason to reject it.

        The solves come first: a solve that ends with `SolveStatus.FUNCTION_ERROR`, where f fails inside the interval,
        rejects the candidate before snuffled runs. snuffled's analyses then run in the order of their tuples, and the
        first one whose diagnostics reject the candidate stops them.
        """
        # --- empirical block --------------------
        solve_results = BenchmarkTask(
            problem_id=problem_id,
            c_min=c_min,
            c_max=c_max,
            solver_ids=self.solver_ids,
            run_settings=BenchmarkRunSettings(
                mc_size=self.fidelity.solves_mc_size,
                n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
                root_seed=PIPELINE_ROOT_SEED,
            ),
        ).run()
        if (solve_results["status"] == SolveStatus.FUNCTION_ERROR.value).any():
            return RejectionReason.FUNCTION_ERROR
        # Every solve without a correct answer counts at the full evaluation budget, `max_fevals`.
        max_fevals = int(solve_results["max_fevals"][0])
        # The rows run sample by sample, and within a sample, solver by solver in the order of `solver_ids`.
        n_fevals_eff = add_derived_results(solve_results)["n_fevals_eff"].to_numpy().reshape(-1, len(self.solver_ids))
        empirical_features = [
            *np.exp(np.log(n_fevals_eff).mean(axis=0)),
            *(gpq(n_fevals_eff.ravel(), level) for level in EMPIRICAL_GPQ_LEVELS),
        ]

        # --- analytical block -------------------
        problem = FormulaRegistry.candidate_from_id(problem_id).calibrated(c_min, c_max)
        mc_solve_settings = MCSolveSettings.from_test_problem(
            problem,
            n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
            mc_tuples=load_mc_tuples(self.fidelity.snuffled_mc_size),
        )
        property_values = []
        for mc_sample_idx in range(self.fidelity.snuffled_mc_size):
            snuffler = self.fidelity.snuffled_budget.build_snuffler(
                problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx
            )
            result = extract_properties_or_rejection_reason(
                snuffler, ANALYTICAL_PROPERTIES, xtol=float(mc_solve_settings.xtols[mc_sample_idx])
            )
            if isinstance(result, RejectionReason):
                return result
            property_values.append(list(result.values()))
        analytical_features = np.mean(property_values, axis=0)

        # --- feature vector ---------------------
        values = [
            *(self._normalize_n_fevals_eff(value, max_fevals) for value in empirical_features),
            *analytical_features,
        ]
        return dict(zip(self.fidelity.feature_column_names(self.solver_ids), map(float, values), strict=True))

    @staticmethod
    def _normalize_n_fevals_eff(value: float, max_fevals: int) -> float:
        """Return `value`, a summary of `n_fevals_eff`, mapped from ``[2, max_fevals]`` onto ``[0, 1]`` on a log scale.

        A correct solve takes at least 2 evaluations, 1 at each interval bound, and a solve without a correct answer
        counts as `max_fevals`, so the result is ``log(value / 2) / log(max_fevals / 2)``.
        """
        return float(np.log(value / 2) / np.log(max_fevals / 2))
