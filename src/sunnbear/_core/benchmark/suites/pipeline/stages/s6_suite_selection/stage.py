"""`SuiteSelectionStage` selects the suites of 2 disjoint series of benchmark suites: the a-series and the b-series."""

from collections.abc import Collection

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.benchmark_suite import SB_A_SERIES, SB_B_SERIES, BenchmarkSuiteSeries
from sunnbear._core.benchmark.suites.pipeline.core import (
    PIPELINE_ROOT_SEED,
    PipelineStage,
    PipelineStageId,
    PipelineStopError,
)
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CandidatePool,
    DifficultyTierQuotas,
    compute_diversity_score,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.state import SuiteSelectionDetails, SuiteSelectionStateAccessor
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  SuiteSelectionStage
# ==================================================================================================
class SuiteSelectionStage(PipelineStage[SuiteSelectionStateAccessor]):
    """`SuiteSelectionStage` selects the suites of `SB_A_SERIES` and `SB_B_SERIES` from the candidates.

    The stage selects 1 suite per size that a series declares, up to the size of the largest suites, which the first
    step below chooses, and builds each suite through its series. Each suite of a series holds every test problem of
    the series' smaller suites, and the 2 series share no test problem.

    The stage stores each candidate's difficulty tier, which `CandidatePool.difficulty_tiers` derives from the EDI that
    fine characterization stored, then selects the suites in 3 steps:

    - **the largest suites:** their size is the largest size that both series declare and that is at most half the
      number of candidates. The largest suite of the a-series is selected from all candidates. The largest suite of
      the b-series comes from a selection, from the same candidates, of twice its size that must hold the largest suite
      of the a-series; the b-series' suite is the half of that selection outside the a-series' suite, so it lies far
      from the a-series' suite and is diverse in itself;
    - **the drops:** the stage drops each candidate that neither largest suite holds; such a candidate is valid, but
      not kept;
    - **the smaller suites:** per series, the suite of each smaller size that the series declares, from the largest to
      the smallest, is selected from the series' next larger suite.

    Every suite is selected by `select_diverse_problem_ids`, under the quotas of its size, with the tiers that
    `DifficultyTierAssignment.from_pool` assigns, for that selection only, to the candidates eligible for the suite.

    The candidates eligible for a suite are those that it is selected from; for the largest suite of the b-series, the
    candidates of the largest suite of the a-series are not eligible.

    The largest suite of the a-series is selected first, so where a tier has too few candidates for both largest
    suites, the a-series' suite still holds that tier's full quota, and the b-series' suite fills the rest of that
    quota with candidates of a neighboring tier.

    Each suite's diversity score is the score of its own test problems, by `compute_diversity_score`.

    The suites of a run ship only when its largest suites have the largest size that both series declare, and every
    candidate of those 2 suites counts toward the quota of the difficulty tier of its EDI.

    The suites of any other run are interim and never ship as benchmark suites.
    """

    stage_id = PipelineStageId.SUITE_SELECTION

    def __init__(self, sec_per_candidate: float = DEFAULT_SELECTION_SEC_PER_CANDIDATE) -> None:
        """Create the stage, whose max-div workers run `sec_per_candidate` seconds per candidate of a search's pool."""
        self.sec_per_candidate = sec_per_candidate
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.SUITE_SELECTION)

    @property
    def parameters(self) -> dict[str, float | int]:
        """Return the time per candidate and the seed of max-div's searches."""
        return {"sec_per_candidate": self.sec_per_candidate, "seed": self.seed}

    def run(self, state_accessor: SuiteSelectionStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Store each candidate's tier, select the suites, drop the other candidates, and store each suite's details.

        max-div uses the number of workers of `worker_pool`, but starts its own worker processes, so the pool's
        workers stay idle.

        Raises:
            PipelineStopError: If there are fewer candidates than twice the smallest size that both series declare, or
                if a selection misses a required candidate or a quota, as `select_diverse_problem_ids` describes.
        """
        # --- size and tiers ---------------------
        largest_suite_size = self._choose_largest_suite_size(len(state_accessor.remaining_problem_ids))
        candidate_pool = state_accessor.candidate_pool()
        state_accessor.set_difficulty_tiers(candidate_pool.difficulty_tiers)

        # --- largest suites ---------------------
        largest_a_series_details = self._select_suite_details(
            candidate_pool, series=SB_A_SERIES, size=largest_suite_size, worker_pool=worker_pool
        )
        largest_b_series_details = self._select_suite_details(
            candidate_pool,
            series=SB_B_SERIES,
            size=largest_suite_size,
            required_problem_ids=largest_a_series_details.benchmark_suite.problem_ids,
            worker_pool=worker_pool,
        )

        # --- drops ------------------------------
        kept_problem_id_set = {
            *largest_a_series_details.benchmark_suite.problem_ids,
            *largest_b_series_details.benchmark_suite.problem_ids,
        }
        for problem_id in state_accessor.remaining_problem_ids:
            if problem_id not in kept_problem_id_set:
                state_accessor.drop(problem_id, "not_in_any_suite")

        # --- smaller suites ---------------------
        all_selection_details: list[SuiteSelectionDetails] = []
        for series, largest_details in (
            (SB_A_SERIES, largest_a_series_details),
            (SB_B_SERIES, largest_b_series_details),
        ):
            selection_details = largest_details
            all_selection_details.append(selection_details)
            for size in sorted((size for size in series.sizes if size < largest_suite_size), reverse=True):
                selection_details = self._select_suite_details(
                    candidate_pool.subset(selection_details.benchmark_suite.problem_ids),
                    series=series,
                    size=size,
                    worker_pool=worker_pool,
                )
                all_selection_details.append(selection_details)
        state_accessor.set_suite_selection_details(all_selection_details)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_suite_details(
        self,
        candidate_pool: CandidatePool,
        *,
        series: BenchmarkSuiteSeries,
        size: int,
        required_problem_ids: Collection[ProblemId] = (),
        worker_pool: WorkerPool,
    ) -> SuiteSelectionDetails:
        """Return the details of the suite of `size` in `series`, chosen from `candidate_pool`.

        The selection also holds every candidate of `required_problem_ids`; the suite holds only the selected candidates
        that are not required.
        """
        required_problem_id_set = set(required_problem_ids)
        selected_problem_ids, tier_assignment = select_diverse_problem_ids(
            candidate_pool,
            quotas=DifficultyTierQuotas(size),
            required_problem_ids=required_problem_id_set,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        suite_problem_ids = [
            problem_id for problem_id in selected_problem_ids if problem_id not in required_problem_id_set
        ]
        return SuiteSelectionDetails(
            benchmark_suite=series.build_suite(suite_problem_ids),
            edi_range_by_tier=tier_assignment.edi_range_by_tier,
            diversity=compute_diversity_score(candidate_pool.subset(suite_problem_ids)),
        )

    @staticmethod
    def _choose_largest_suite_size(n_candidates: int) -> int:
        """Return the size of each series' largest suite for `n_candidates` candidates.

        The size is the largest size that both `SB_A_SERIES` and `SB_B_SERIES` declare and that is at most half of
        `n_candidates`, because the 2 largest suites share no candidate.

        Raises:
            PipelineStopError: If `n_candidates` is less than twice the smallest size that both series declare.
        """
        common_sizes = sorted(set(SB_A_SERIES.sizes) & set(SB_B_SERIES.sizes))
        smallest_common_size = common_sizes[0]
        if n_candidates < 2 * smallest_common_size:
            raise PipelineStopError(
                f"There are {n_candidates} candidates, fewer than the {2 * smallest_common_size} that 2 benchmark "
                f"suites of {smallest_common_size} test problems need."
            )
        else:
            return max(size for size in common_sizes if 2 * size <= n_candidates)
