"""`DistillationStage` distills 2 disjoint families of nested suites from the Core: benchmark and calibration suites."""

from typing import TYPE_CHECKING

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CandidatePool,
    DiverseSuite,
    SuiteComposition,
    SuiteFamily,
    select_diverse_suite,
)
from sunnbear._core.benchmark.suites.pipeline.state import (
    DistillationStateAccessor,
    DistilledSuiteSummary,
    SuiteMembership,
)
from sunnbear._core.utils.worker_pool import WorkerPool

if TYPE_CHECKING:
    from sunnbear._core.problems.core import ProblemId

# Each family holds 1 suite per power of 2 from this size up to half the Core.
SMALLEST_SUITE_SIZE = 64


# ==================================================================================================
#  DistillationStage
# ==================================================================================================
class DistillationStage(PipelineStage[DistillationStateAccessor]):
    """`DistillationStage` distills 2 families of suites from the Core: benchmark suites and calibration suites.

    Each family holds 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to half the Core, and each of its suites
    holds every candidate of the family's smaller suites. The 2 families share no candidate. Every suite has the Core's
    composition, scaled to its size.

    The stage distills the suites in 2 steps, each suite selected by `select_diverse_suite`:

    - **the split:** the largest benchmark suite is selected from the Core, with half of each of the Core's quotas. The
      rest of the Core is the largest calibration suite, which meets the same quotas, because each of the Core's quotas
      is twice the matching quota of the largest benchmark suite;
    - **the halvings:** per family, each smaller suite is selected from the family's next larger suite, with half of
      each of that larger suite's quotas.
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
        """Distill the suites from the Core, and store each member's `SuiteMembership` and each suite's summary.

        max-div uses the number of workers of `worker_pool`, but starts its own worker processes, so the pool's
        workers stay idle.

        Raises:
            PipelineStopError: If a selection misses a quota, as `select_diverse_suite` describes.
        """
        core_pool = state_accessor.candidate_pool()

        # --- split ------------------------------
        largest_suite_composition = state_accessor.core_composition().halved()
        largest_benchmark_suite = self._select_suite(
            core_pool, largest_suite_composition, n_workers=worker_pool.n_workers
        )
        largest_benchmark_problem_ids = set(largest_benchmark_suite.problem_ids)
        largest_calibration_problem_ids = tuple(
            problem_id
            for problem_id in core_pool.feature_matrix.problem_ids
            if problem_id not in largest_benchmark_problem_ids
        )

        # --- halvings ---------------------------
        suite_memberships: dict[ProblemId, SuiteMembership] = {}
        distilled_suite_summaries: list[DistilledSuiteSummary] = []
        for family, largest_suite_problem_ids, largest_suite_diversity in [
            (SuiteFamily.BENCHMARK, largest_benchmark_suite.problem_ids, largest_benchmark_suite.diversity),
            # No max-div run selects the largest calibration suite, so it has no diversity score.
            (SuiteFamily.CALIBRATION, largest_calibration_problem_ids, None),
        ]:
            smallest_containing_suite_sizes = dict.fromkeys(largest_suite_problem_ids, largest_suite_composition.size)
            distilled_suite_summaries.append(
                DistilledSuiteSummary(
                    suite_family=family, size=len(largest_suite_problem_ids), diversity=largest_suite_diversity
                )
            )
            suite_problem_ids, composition = largest_suite_problem_ids, largest_suite_composition
            while composition.size > SMALLEST_SUITE_SIZE:
                composition = composition.halved()
                suite = self._select_suite(
                    core_pool.subset(suite_problem_ids), composition, n_workers=worker_pool.n_workers
                )
                suite_problem_ids = suite.problem_ids
                smallest_containing_suite_sizes.update(dict.fromkeys(suite_problem_ids, composition.size))
                distilled_suite_summaries.append(
                    DistilledSuiteSummary(suite_family=family, size=len(suite_problem_ids), diversity=suite.diversity)
                )
            suite_memberships.update(
                {
                    problem_id: SuiteMembership(suite_family=family, smallest_containing_suite_size=size)
                    for problem_id, size in smallest_containing_suite_sizes.items()
                }
            )
        state_accessor.set_suite_memberships(suite_memberships)
        state_accessor.set_distilled_suite_summaries(distilled_suite_summaries)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_suite(
        self, candidate_pool: CandidatePool, composition: SuiteComposition, *, n_workers: int
    ) -> DiverseSuite:
        """Return the suite of `composition` that max-div selects from `candidate_pool`, with the stage's settings."""
        return select_diverse_suite(
            candidate_pool,
            composition=composition,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=n_workers,
        )
