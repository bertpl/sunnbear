"""`DistillationStage` distills 2 disjoint series of nested suites from the Core: the a-series and the b-series."""

from collections import Counter
from collections.abc import Sequence

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuite
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CandidatePool,
    DifficultyTierQuotas,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.state import DistillationStateAccessor, SuiteSelectionDetails
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

# Each series holds 1 suite per power of 2 from this size up to half the Core.
SMALLEST_SUITE_SIZE = 64
# The suites of the primary series carry these aliases, by size; a run whose Core is smaller than 2048 produces no suite
# of the larger sizes, and so none of their aliases either.
_PRIMARY_SERIES_ALIASES = {
    1024: ("sb-large",),
    512: ("sb-medium",),
    256: ("sb-small",),
    128: ("sb-xsmall",),
    64: ("sb-tiny",),
}


# ==================================================================================================
#  DistillationStage
# ==================================================================================================
class DistillationStage(PipelineStage[DistillationStateAccessor]):
    """`DistillationStage` distills 2 series of suites from the Core: the primary series and the secondary series.

    Each series holds 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to half the Core, and each of its suites
    holds every candidate of the series' smaller suites. The 2 series share no candidate. The primary series' suites
    are named `sb-<size>a` and carry the aliases of `_PRIMARY_SERIES_ALIASES`; the secondary series' are named
    `sb-<size>b`.

    The stage distills the suites in 2 steps, each suite selected by `select_diverse_problem_ids`, under quotas that
    `DifficultyTierQuotas.resolve` chooses anew for each selection, at the suite's size and from the candidates that it
    is selected from:

    - **the split:** the largest suite of the primary series is selected from the Core. The rest of the Core is the
      largest suite of the secondary series, which no selection makes;
    - **the halvings:** per series, each smaller suite is selected from the series' next larger suite.
    """

    stage_id = PipelineStageId.DISTILLATION

    def __init__(self, sec_per_candidate: float = DEFAULT_SELECTION_SEC_PER_CANDIDATE) -> None:
        """Create the stage, whose max-div workers run `sec_per_candidate` seconds per candidate of a search's pool."""
        self.sec_per_candidate = sec_per_candidate
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.DISTILLATION)

    @property
    def parameters(self) -> dict[str, float | int]:
        """Return the time per candidate and the seed of max-div's searches."""
        return {"sec_per_candidate": self.sec_per_candidate, "seed": self.seed}

    def run(self, state_accessor: DistillationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Distill the suites from the Core, and store each suite's `SuiteSelectionDetails`.

        max-div uses the number of workers of `worker_pool`, but starts its own worker processes, so the pool's
        workers stay idle.

        Raises:
            PipelineStopError: If a selection misses a quota, as `select_diverse_problem_ids` describes.
        """
        core_pool = state_accessor.candidate_pool()

        # --- split ------------------------------
        largest_suite_size = len(core_pool.feature_matrix.problem_ids) // 2
        largest_primary_suite = self._select_suite(
            core_pool, size=largest_suite_size, is_primary=True, worker_pool=worker_pool
        )
        largest_primary_problem_ids = set(largest_primary_suite.benchmark_suite.problem_ids)
        largest_secondary_suite = SuiteSelectionDetails(
            benchmark_suite=self._build_suite(
                [p for p in core_pool.feature_matrix.problem_ids if p not in largest_primary_problem_ids],
                is_primary=False,
            ),
            tier_quotas=None,
            diversity=None,
        )

        # --- halvings ---------------------------
        all_selection_details: list[SuiteSelectionDetails] = []
        for is_primary, largest_suite in ((True, largest_primary_suite), (False, largest_secondary_suite)):
            selection_details = largest_suite
            all_selection_details.append(selection_details)
            while selection_details.benchmark_suite.size > SMALLEST_SUITE_SIZE:
                selection_details = self._select_suite(
                    core_pool.subset(selection_details.benchmark_suite.problem_ids),
                    size=selection_details.benchmark_suite.size // 2,
                    is_primary=is_primary,
                    worker_pool=worker_pool,
                )
                all_selection_details.append(selection_details)
        state_accessor.set_distilled_suite_selection_details(
            {details.benchmark_suite.name: details for details in all_selection_details}
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_suite(
        self, pool: CandidatePool, *, size: int, is_primary: bool, worker_pool: WorkerPool
    ) -> SuiteSelectionDetails:
        """Return the details of a suite of `size` of the primary or secondary series, selected from `pool`."""
        tier_quotas = DifficultyTierQuotas.resolve(size, Counter(pool.difficulty_tiers))
        problem_ids, diversity = select_diverse_problem_ids(
            pool,
            tier_quotas=tier_quotas,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        return SuiteSelectionDetails(
            benchmark_suite=self._build_suite(problem_ids, is_primary=is_primary),
            tier_quotas=tier_quotas,
            diversity=diversity,
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
