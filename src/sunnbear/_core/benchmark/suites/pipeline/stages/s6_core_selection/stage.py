"""`CoreSelectionStage` selects the Core: the most diverse candidates, at the largest size that the candidates fill."""

from collections import Counter

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuite
from sunnbear._core.benchmark.suites.pipeline.core import (
    PIPELINE_ROOT_SEED,
    PipelineStage,
    PipelineStageId,
    PipelineStopError,
)
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    DifficultyTier,
    DifficultyTierQuotas,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.state import CoreSelectionStateAccessor, SuiteSelectionDetails
from sunnbear._core.utils.worker_pool import WorkerPool

# Every Core size is a power of 2, so that every suite distilled from the Core, of half its size or a further half, has
# whole quotas. The Core that ships has the largest size, with a quota per tier; any other Core is interim.
CORE_SIZES = (128, 256, 512, 1024, 2048)


# ==================================================================================================
#  CoreSelectionStage
# ==================================================================================================
class CoreSelectionStage(PipelineStage[CoreSelectionStateAccessor]):
    """`CoreSelectionStage` selects the Core, the suite `sb-<size>`; every other benchmark suite is selected from it.

    A candidate's tier follows from the EDI that full characterization stored, relative to
    `DEFAULT_N_BISECTION_FEVALS`, the `n_bisection_fevals` with which the characterization stages run every solve.

    The stage selects the Core in 3 steps:

    - the Core's size is the largest of `CORE_SIZES` that the candidates fill, whatever their tiers; below the smallest
      size, the stage stops the pipeline;
    - `DifficultyTierQuotas.resolve` chooses the Core's quotas, merged until the candidates can meet each of them;
    - `select_diverse_problem_ids` selects the Core by max-div.

    The stage drops each candidate that the Core does not hold; such a candidate is valid, but not kept.
    """

    stage_id = PipelineStageId.CORE_SELECTION

    def __init__(self, sec_per_candidate: float = DEFAULT_SELECTION_SEC_PER_CANDIDATE) -> None:
        """Create the stage, whose max-div workers each run for `sec_per_candidate` seconds per input candidate."""
        self.sec_per_candidate = sec_per_candidate
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.CORE_SELECTION)

    @property
    def parameters(self) -> dict[str, float | int]:
        """Return the time per candidate and the seed of max-div's search."""
        return {"sec_per_candidate": self.sec_per_candidate, "seed": self.seed}

    def run(self, state_accessor: CoreSelectionStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Store each candidate's tier, select the Core, drop the other candidates, and store the Core's details.

        max-div uses the number of workers of `worker_pool`, but starts its own worker processes, so the pool's
        workers stay idle.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest of `CORE_SIZES`, or if max-div's
                selection misses a quota, as `select_diverse_problem_ids` describes.
        """
        # --- difficulty tiers -------------------
        difficulty_tiers = {
            problem_id: DifficultyTier.from_edi(edi, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
            for problem_id, edi in state_accessor.edis().items()
        }
        state_accessor.set_difficulty_tiers(difficulty_tiers)

        # --- size and quotas --------------------
        core_size = self._choose_core_size(len(difficulty_tiers))
        tier_quotas = DifficultyTierQuotas.resolve(core_size, Counter(difficulty_tiers.values()))

        # --- selection --------------------------
        core_problem_ids, diversity = select_diverse_problem_ids(
            state_accessor.candidate_pool(),
            tier_quotas=tier_quotas,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        core_problem_id_set = set(core_problem_ids)
        for problem_id in state_accessor.remaining_problem_ids:
            if problem_id not in core_problem_id_set:
                state_accessor.drop(problem_id, "not_in_core")
        state_accessor.set_core_selection_details(
            SuiteSelectionDetails(
                benchmark_suite=BenchmarkSuite(name=f"sb-{core_size}", aliases=(), problem_ids=core_problem_ids),
                tier_quotas=tier_quotas,
                diversity=diversity,
            )
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _choose_core_size(n_candidates: int) -> int:
        """Return the largest of `CORE_SIZES` that `n_candidates` candidates fill.

        Raises:
            PipelineStopError: If `n_candidates` is below the smallest of `CORE_SIZES`.
        """
        core_size = max((size for size in CORE_SIZES if size <= n_candidates), default=None)
        if core_size is None:
            raise PipelineStopError(
                f"The candidates fill no Core of {min(CORE_SIZES)} or more: there are {n_candidates}."
            )
        else:
            return core_size
