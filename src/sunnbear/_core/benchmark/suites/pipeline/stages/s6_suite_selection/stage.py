"""`SuiteSelectionStage` selects the suites of every built-in series of benchmark suites."""

from collections.abc import Collection, Sequence
from fractions import Fraction

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.benchmark_suite import PUB_SERIES, SB_A_SERIES, SB_B_SERIES, BenchmarkSuiteSeries
from sunnbear._core.benchmark.suites.pipeline.core import (
    PIPELINE_ROOT_SEED,
    PipelineStage,
    PipelineStageId,
    PipelineStopError,
)
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CandidatePool,
    DifficultyTier,
    DifficultyTierCandidateGroup,
    FormulaCategoryCandidateGroup,
    ShareQuota,
    compute_diversity_score,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.state import SuiteSelectionDetails, SuiteSelectionStateAccessor
from sunnbear._core.problems.catalog.c01_published_test_problems import PublishedTestProblems
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

from .series_selection_spec import SeriesSelectionSpec

# Each difficulty tier holds exactly a quarter of every suite of the a-series and the b-series, so that each suite
# spreads its test problems evenly over the range of difficulties; a candidate counts toward the quota of its own
# difficulty tier.
_DIFFICULTY_TIER_QUOTAS = tuple(
    ShareQuota.exactly(DifficultyTierCandidateGroup(tiers=(tier,)), Fraction(1, 4)) for tier in DifficultyTier
)
_SB_A_SERIES_SPEC = SeriesSelectionSpec(series=SB_A_SERIES, quotas=_DIFFICULTY_TIER_QUOTAS)
_SB_B_SERIES_SPEC = SeriesSelectionSpec(series=SB_B_SERIES, quotas=_DIFFICULTY_TIER_QUOTAS)
# The pub-series holds the test problems of category 1 alone, and has no quotas.
_PUB_SERIES_SPEC = SeriesSelectionSpec(
    series=PUB_SERIES, candidate_group=FormulaCategoryCandidateGroup(category=PublishedTestProblems)
)
# The stage stores the suites of each series in the order of these specs, which is the order of `BUILT_IN_SERIES`.
_SERIES_SELECTION_SPECS = (_SB_A_SERIES_SPEC, _SB_B_SERIES_SPEC, _PUB_SERIES_SPEC)


# ==================================================================================================
#  SuiteSelectionStage
# ==================================================================================================
class SuiteSelectionStage(PipelineStage[SuiteSelectionStateAccessor]):
    """`SuiteSelectionStage` selects the suites of every built-in series from the candidates.

    The stage selects 1 suite per size that a series declares, up to the size of the series' largest suite, and
    creates each suite through its series. Each suite of a series holds every test problem of the series' smaller
    suites. The a-series and the b-series share no test problem, and the pub-series may share test problems with both.

    The stage stores each candidate's difficulty tier, which `CandidatePool.difficulty_tiers` derives from the EDI that
    fine characterization stored, then selects the suites in 3 steps:

    - **the largest suites:**

      - the largest suites of the a-series and the b-series have the largest size that both series declare and that is
        at most half the number of candidates;
      - the largest suite of the a-series is selected from all candidates;
      - the largest suite of the b-series comes from a selection, from the same candidates, of twice its size that
        must hold the largest suite of the a-series; the b-series' suite is the half of that selection outside the
        a-series' suite, so it lies far from the a-series' suite and is diverse in itself;
      - the largest suite of the pub-series has the largest size that the series declares and that is at most the
        number of candidates of category 1, from which it is selected; the a-series and the b-series do not affect it.
        With fewer candidates of category 1 than its smallest size, the pub-series has no suite;

    - **the drops:** the stage drops each candidate that no largest suite holds; such a candidate is valid, but not
      kept;
    - **the smaller suites:** per series, the suite of each smaller size that the series declares, from the largest to
      the smallest, is selected from the series' next larger suite.

    Every suite is selected by `select_diverse_problem_ids`, from the members of the candidate group of its series'
    `SeriesSelectionSpec`, under the spec's quotas. The largest suite of the a-series is selected first, so where a
    tier has too few candidates for both largest suites, the a-series' suite meets that tier's quota, and the
    b-series' suite misses it.

    max-div then fills the b-series' suite with candidates of other tiers, and the suite's selection details record
    that it misses the quota.

    Each suite's diversity score is the score of its own test problems, by `compute_diversity_score`.

    The suites of a run ship only when every series' largest suite has the largest size that its series declares, and
    every suite meets every quota; the suites of any other run are interim.
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
            PipelineStopError: If there are fewer candidates than twice the smallest size that both the a-series and
                the b-series declare, or if a selection misses a required candidate, as `select_diverse_problem_ids`
                describes.
        """
        # --- sizes and tiers --------------------
        n_candidates = len(state_accessor.remaining_problem_ids)
        sb_suite_size = self._choose_largest_suite_size(n_candidates, disjoint_series=(SB_A_SERIES, SB_B_SERIES))
        if sb_suite_size is None:
            smallest_sb_suite_size = min(set(SB_A_SERIES.sizes) & set(SB_B_SERIES.sizes))
            raise PipelineStopError(
                f"There are {n_candidates} candidates, fewer than the {2 * smallest_sb_suite_size} that 2 benchmark "
                f"suites of {smallest_sb_suite_size} test problems need."
            )
        candidate_pool = state_accessor.candidate_pool()
        state_accessor.set_difficulty_tiers(candidate_pool.difficulty_tiers)
        pub_suite_size = self._choose_largest_suite_size(
            len(_PUB_SERIES_SPEC.restrict_pool(candidate_pool)), disjoint_series=(PUB_SERIES,)
        )

        # --- largest suites ---------------------
        largest_a_series_details = self._select_suite_details(
            candidate_pool, spec=_SB_A_SERIES_SPEC, size=sb_suite_size, worker_pool=worker_pool
        )
        largest_details_by_series_id = {
            SB_A_SERIES.series_id: largest_a_series_details,
            SB_B_SERIES.series_id: self._select_suite_details(
                candidate_pool,
                spec=_SB_B_SERIES_SPEC,
                size=sb_suite_size,
                required_problem_ids=largest_a_series_details.benchmark_suite.problem_ids,
                worker_pool=worker_pool,
            ),
        }
        if pub_suite_size is not None:
            largest_details_by_series_id[PUB_SERIES.series_id] = self._select_suite_details(
                candidate_pool, spec=_PUB_SERIES_SPEC, size=pub_suite_size, worker_pool=worker_pool
            )

        # --- drops ------------------------------
        kept_problem_id_set = {
            problem_id
            for selection_details in largest_details_by_series_id.values()
            for problem_id in selection_details.benchmark_suite.problem_ids
        }
        for problem_id in state_accessor.remaining_problem_ids:
            if problem_id not in kept_problem_id_set:
                state_accessor.drop(problem_id, "not_in_any_suite")

        # --- smaller suites ---------------------
        all_selection_details: list[SuiteSelectionDetails] = []
        for spec in _SERIES_SELECTION_SPECS:
            if spec.series.series_id in largest_details_by_series_id:
                selection_details = largest_details_by_series_id[spec.series.series_id]
                largest_suite_size = len(selection_details.benchmark_suite.problem_ids)
                all_selection_details.append(selection_details)
                for size in sorted((size for size in spec.series.sizes if size < largest_suite_size), reverse=True):
                    selection_details = self._select_suite_details(
                        candidate_pool.subset(selection_details.benchmark_suite.problem_ids),
                        spec=spec,
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
        spec: SeriesSelectionSpec,
        size: int,
        required_problem_ids: Collection[ProblemId] = (),
        worker_pool: WorkerPool,
    ) -> SuiteSelectionDetails:
        """Return the details of the suite of `size` in the series of `spec`, chosen from `candidate_pool`.

        The suite holds only members of the spec's candidate group, under the spec's quotas. The selection also holds
        every candidate of `required_problem_ids`; the suite holds only the selected candidates that are not required.
        """
        required_problem_id_set = set(required_problem_ids)
        selected_problem_ids, quota_fulfillments = select_diverse_problem_ids(
            spec.restrict_pool(candidate_pool),
            selection_size=size,
            quotas=spec.quotas,
            required_problem_ids=required_problem_id_set,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        suite_problem_ids = [
            problem_id for problem_id in selected_problem_ids if problem_id not in required_problem_id_set
        ]
        return SuiteSelectionDetails(
            benchmark_suite=spec.series.create_suite(suite_problem_ids),
            quota_fulfillments=quota_fulfillments,
            diversity=compute_diversity_score(candidate_pool.subset(suite_problem_ids)),
        )

    @staticmethod
    def _choose_largest_suite_size(n_candidates: int, *, disjoint_series: Sequence[BenchmarkSuiteSeries]) -> int | None:
        """Return the size of the largest suite of each series of `disjoint_series` for `n_candidates` candidates.

        The largest suites of `disjoint_series` share no candidate, so their size is the largest size that each of
        these series declares and at which that many suites fit into `n_candidates`: for 2 series, at most half of
        `n_candidates`. Return None when not even the smallest such size fits.
        """
        common_sizes = set.intersection(*(set(series.sizes) for series in disjoint_series))
        fitting_sizes = [size for size in common_sizes if len(disjoint_series) * size <= n_candidates]
        if fitting_sizes:
            return max(fitting_sizes)
        else:
            return None
