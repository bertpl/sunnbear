"""`SuiteSelectionStage` selects 2 disjoint series of nested benchmark suites: the a-series and the b-series."""

from collections.abc import Collection, Sequence

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuite
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

# Each series holds 1 suite per power of 2 from this size up to the size of its largest suite.
SMALLEST_SUITE_SIZE = 64
# The largest suite of each series holds at most this many test problems. `MAX_SUITE_SIZE` is `SMALLEST_SUITE_SIZE`
# times a power of 2, so that every suite of a series, whose size is the largest suite's divided by a power of 2, has
# whole quotas.
#
# The suites of a run ship only when its largest suites have this size and every candidate of those 2 suites counts
# toward the quota of its own difficulty tier. The suites of any other run are interim and never ship as benchmark
# suites.
MAX_SUITE_SIZE = 1024
# The suites of the primary series, the a-series, carry these aliases, by size; a run whose largest suites are smaller
# than `MAX_SUITE_SIZE` produces no suite of the larger sizes, and so none of their aliases either.
_PRIMARY_SERIES_ALIASES = {
    1024: ("sb-large",),
    512: ("sb-medium",),
    256: ("sb-small",),
    128: ("sb-xsmall",),
    64: ("sb-tiny",),
}


# ==================================================================================================
#  SuiteSelectionStage
# ==================================================================================================
class SuiteSelectionStage(PipelineStage[SuiteSelectionStateAccessor]):
    """`SuiteSelectionStage` selects 2 series of suites from the candidates: the a-series and the b-series.

    Each series holds 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to the size of its largest suite, and each
    of its suites holds every test problem of the series' smaller suites. The 2 series share no test problem.

    The primary series, the a-series, names its suites `sb-<size>a` and gives them the aliases of
    `_PRIMARY_SERIES_ALIASES`; the secondary series, the b-series, names its suites `sb-<size>b`.

    The stage stores each candidate's difficulty tier, which `CandidatePool.difficulty_tiers` derives from the EDI that
    fine characterization stored, then selects the suites in 3 steps:

    - **the largest suites:** their size is the largest power of 2 from `SMALLEST_SUITE_SIZE` up to `MAX_SUITE_SIZE`
      that the candidates fill twice. The largest suite of the primary series is selected from all candidates. The
      largest suite of the secondary series is selected from the same candidates, by a selection of twice its size
      that must hold the primary suite: the secondary suite is the half that the primary suite does not hold, so it
      lies far from the primary suite and is diverse in itself;
    - **the drops:** the stage drops each candidate that neither largest suite holds; such a candidate is valid, but
      not kept;
    - **the halvings:** per series, each smaller suite is selected from the series' next larger suite.

    Every suite is selected by `select_diverse_problem_ids`, under the quotas of its size, with the tiers that
    `DifficultyTierAssignment.from_pool` assigns anew to the candidates eligible for the suite: for the largest suite
    of the secondary series, all candidates but those of the largest primary suite.

    The primary series selects first, so where a tier has too few candidates for both largest suites, the primary
    suite still holds that tier's full quota, and the secondary suite fills the rest of that quota with candidates of
    a neighboring tier. Each suite's diversity score is the score of its own test problems, by
    `compute_diversity_score`.
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
            PipelineStopError: If the candidates fill no 2 suites of `SMALLEST_SUITE_SIZE`, or if a selection misses a
                required candidate or a quota, as `select_diverse_problem_ids` describes.
        """
        # --- size and tiers ---------------------
        largest_suite_size = self._choose_largest_suite_size(len(state_accessor.remaining_problem_ids))
        candidate_pool = state_accessor.candidate_pool()
        state_accessor.set_difficulty_tiers(candidate_pool.difficulty_tiers)

        # --- largest suites ---------------------
        largest_primary_details = self._select_suite_details(
            candidate_pool, size=largest_suite_size, is_primary=True, worker_pool=worker_pool
        )
        largest_secondary_details = self._select_suite_details(
            candidate_pool,
            size=largest_suite_size,
            is_primary=False,
            required_problem_ids=largest_primary_details.benchmark_suite.problem_ids,
            worker_pool=worker_pool,
        )

        # --- drops ------------------------------
        kept_problem_id_set = {
            *largest_primary_details.benchmark_suite.problem_ids,
            *largest_secondary_details.benchmark_suite.problem_ids,
        }
        for problem_id in state_accessor.remaining_problem_ids:
            if problem_id not in kept_problem_id_set:
                state_accessor.drop(problem_id, "not_in_any_suite")

        # --- halvings ---------------------------
        all_selection_details: list[SuiteSelectionDetails] = []
        for is_primary, largest_details in ((True, largest_primary_details), (False, largest_secondary_details)):
            selection_details = largest_details
            all_selection_details.append(selection_details)
            while len(selection_details.benchmark_suite.problem_ids) > SMALLEST_SUITE_SIZE:
                selection_details = self._select_suite_details(
                    candidate_pool.subset(selection_details.benchmark_suite.problem_ids),
                    size=len(selection_details.benchmark_suite.problem_ids) // 2,
                    is_primary=is_primary,
                    worker_pool=worker_pool,
                )
                all_selection_details.append(selection_details)
        state_accessor.set_suite_selection_details(
            {details.benchmark_suite.name: details for details in all_selection_details}
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_suite_details(
        self,
        candidate_pool: CandidatePool,
        *,
        size: int,
        is_primary: bool,
        required_problem_ids: Collection[ProblemId] = (),
        worker_pool: WorkerPool,
    ) -> SuiteSelectionDetails:
        """Return the details of a suite of `size` in the primary or secondary series, chosen from `candidate_pool`.

        The suite holds the selected candidates that are not in `required_problem_ids`, which the selection holds too.
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
            benchmark_suite=self._build_suite(suite_problem_ids, is_primary=is_primary),
            edi_range_by_tier=tier_assignment.edi_range_by_tier,
            diversity=compute_diversity_score(candidate_pool.subset(suite_problem_ids)),
        )

    @staticmethod
    def _build_suite(problem_ids: Sequence[ProblemId], *, is_primary: bool) -> BenchmarkSuite:
        """Return the suite of `problem_ids` in the primary or the secondary series, with its name and aliases."""
        size = len(problem_ids)
        if is_primary:
            return BenchmarkSuite(
                name=f"sb-{size}a", aliases=_PRIMARY_SERIES_ALIASES.get(size, ()), problem_ids=tuple(problem_ids)
            )
        else:
            return BenchmarkSuite(name=f"sb-{size}b", aliases=(), problem_ids=tuple(problem_ids))

    @staticmethod
    def _choose_largest_suite_size(n_candidates: int) -> int:
        """Return the size of each series' largest suite, which `n_candidates` candidates fill twice.

        The size is the largest power of 2 from `SMALLEST_SUITE_SIZE` up to `MAX_SUITE_SIZE` of which the candidates
        fill 2 suites.

        Raises:
            PipelineStopError: If `n_candidates` candidates fill no 2 suites of `SMALLEST_SUITE_SIZE`.
        """
        if n_candidates < 2 * SMALLEST_SUITE_SIZE:
            raise PipelineStopError(
                f"The candidates fill no 2 benchmark suites of {SMALLEST_SUITE_SIZE} test problems or more: there are "
                f"{n_candidates}."
            )
        else:
            largest_suite_size = SMALLEST_SUITE_SIZE
            while 2 * largest_suite_size <= MAX_SUITE_SIZE and 2 * (2 * largest_suite_size) <= n_candidates:
                largest_suite_size *= 2
            return largest_suite_size
