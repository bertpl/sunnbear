"""`CoreSelectionStage` selects the Core: the most diverse candidates, at the largest size whose quotas they fill."""

from collections import Counter

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CoreComposition,
    DifficultyClass,
    select_diverse_suite,
)
from sunnbear._core.benchmark.suites.pipeline.state import CoreSelectionStateAccessor
from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  CoreSelectionStage
# ==================================================================================================
class CoreSelectionStage(PipelineStage[CoreSelectionStateAccessor]):
    """`CoreSelectionStage` selects the Core; every benchmark suite is selected from the Core.

    A candidate's class follows from the EDI that full characterization stored, relative to
    `DEFAULT_N_BISECTION_FEVALS`, the `n_bisection_fevals` with which the characterization stages run every solve.

    The stage selects the Core in 2 steps:

    - `CoreComposition.from_class_counts` chooses the Core's size and difficulty quotas, and stops the pipeline when the
      candidates fill no Core of the smallest size;
    - `select_diverse_suite` selects the Core by max-div, and stops the pipeline when the selection misses a quota.

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
        """Store each candidate's class, select the Core, store its composition, and drop the other candidates.

        max-div uses the number of workers of `worker_pool`, but starts its own worker processes, so the pool's
        workers stay idle.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest size, as
                `CoreComposition.from_class_counts` describes it, or if max-div's selection misses a quota, as
                `select_diverse_suite` describes.
        """
        # --- difficulty classes -----------------
        difficulty_classes = {
            problem_id: DifficultyClass.from_edi(edi, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
            for problem_id, edi in state_accessor.edis().items()
        }
        state_accessor.set_difficulty_classes(difficulty_classes)

        # --- Core size and quotas ---------------
        core_composition = CoreComposition.from_class_counts(Counter(difficulty_classes.values()))

        # --- selection --------------------------
        core = select_diverse_suite(
            state_accessor.candidate_pool(),
            composition=core_composition,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        state_accessor.set_core_composition(core_composition)
        core_problem_ids = set(core.problem_ids)
        for problem_id in state_accessor.remaining_problem_ids:
            if problem_id not in core_problem_ids:
                state_accessor.drop(problem_id, "not_in_core")
