"""`DistillationStage` distills 2 disjoint families of nested suites from the Core: benchmark and calibration suites."""

from collections import Counter
from collections.abc import Sequence

import numpy as np
import polars as pl

from sunnbear._core.benchmark.protocol import SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageOutput
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    CandidatePool,
    DifficultyClass,
    SuiteComposition,
    select_diverse_suite,
)
from sunnbear._core.benchmark.suites.pipeline.stages.s6_core_selection import CoreComposition, CoreSelectionStage
from sunnbear._core.utils.worker_pool import WorkerPool

from .suite_family import SuiteFamily

# The stage adds these columns: each candidate's family, and the size of the smallest suite of that family that holds
# the candidate.
SUITE_MEMBERSHIP_SCHEMA: dict[str, pl.DataType] = {
    "suite_family": pl.Enum([family.value for family in SuiteFamily]),
    "smallest_containing_suite_size": pl.Int64(),
}
SUITE_COMPOSITIONS_REPORT_NAME = "suite_compositions"
# Each family holds 1 suite per power of 2 from this size up to half the Core.
SMALLEST_SUITE_SIZE = 64


# ==================================================================================================
#  DistillationStage
# ==================================================================================================
class DistillationStage(PipelineStage):
    """`DistillationStage` distills 2 families of suites from the Core: benchmark suites and calibration suites.

    Each family holds 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to half the Core, and each of its suites
    holds every candidate of the family's smaller suites. The 2 families share no candidate. Every suite has the Core's
    composition, scaled to its size.

    The Core's composition is read back from its class counts by `CoreComposition.from_class_counts`: the Core meets
    its quotas exactly, so the largest Core that its own candidates fill is the Core itself. Where classes Da and Db
    share 1 quota, `CoreComposition.from_class_counts` warns again, as it did in core selection.

    The stage distills the suites in 2 steps, each suite selected by `select_diverse_suite`:

    - **the split:** the largest benchmark suite is selected from the Core, with half of each of the Core's quotas. The
      rest of the Core is the largest calibration suite, which meets the same quotas, because each of the Core's quotas
      is twice the matching quota of the largest benchmark suite;
    - **the halvings:** per family, each smaller suite is selected from the family's next larger suite, with half of
      each of that larger suite's quotas.
    """

    output_name = "s7_suites"

    def __init__(self, sec_per_candidate: float = DEFAULT_SELECTION_SEC_PER_CANDIDATE) -> None:
        """Create the stage, whose max-div workers each run for `sec_per_candidate` seconds per candidate of a pool."""
        self.sec_per_candidate = sec_per_candidate
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.DISTILLATION)

    @property
    def parameters(self) -> dict[str, float | int]:
        """Return the time per candidate and the seed of max-div's searches."""
        return {"sec_per_candidate": self.sec_per_candidate, "seed": self.seed}

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the Core's candidates with their suite family and smallest suite, and the report on every suite.

        Args:
            previous_table: The output table of `CoreSelectionStage`.
            worker_pool: The worker pool of the run, whose number of workers max-div uses; max-div starts its own
                worker processes, and the pool's workers stay idle.

        Returns:
            The stage's output, which holds:

            - the output table: every row of `previous_table`, in its order, with the columns of
              `SUITE_MEMBERSHIP_SCHEMA`. The suite of size ``n`` of a family is the family's rows whose
              ``smallest_containing_suite_size`` is at most ``n``;
            - the report `SUITE_COMPOSITIONS_REPORT_NAME`: 1 row per suite, the benchmark suites first, each family
              from its largest suite down, with these columns:

              - ``suite_family`` and ``size``: the suite's family and its number of candidates;
              - ``n_candidates_<class>``, with the class's value in lower case: the suite's number of candidates of
                that class;
              - ``diversity``: the score of the max-div run that selected the suite, null for the largest calibration
                suite, which no run selects.

        Raises:
            PipelineStopError: If a selection misses a quota, as `select_diverse_suite` describes.
        """
        pool = CoreSelectionStage.candidate_pool(previous_table)

        # --- split ------------------------------
        largest_suite_composition = CoreComposition.from_class_counts(Counter(pool.difficulty_classes)).halved()
        benchmark_rows, benchmark_diversity = self._select_suite(
            pool, np.arange(previous_table.height), largest_suite_composition, n_workers=worker_pool.n_workers
        )
        calibration_rows = np.setdiff1d(np.arange(previous_table.height), benchmark_rows)

        # --- halvings ---------------------------
        suite_families = np.empty(previous_table.height, dtype=object)
        smallest_containing_suite_sizes = np.full(previous_table.height, largest_suite_composition.size)
        report_rows = []
        for family, largest_suite_rows, largest_suite_diversity in [
            (SuiteFamily.BENCHMARK, benchmark_rows, benchmark_diversity),
            # No max-div run selects the largest calibration suite, so it has no diversity score.
            (SuiteFamily.CALIBRATION, calibration_rows, None),
        ]:
            suite_families[largest_suite_rows] = family.value
            report_rows.append(
                self._report_row(family, largest_suite_rows, largest_suite_diversity, pool.difficulty_classes)
            )
            suite_rows, composition = largest_suite_rows, largest_suite_composition
            while composition.size > SMALLEST_SUITE_SIZE:
                composition = composition.halved()
                suite_rows, diversity = self._select_suite(
                    pool, suite_rows, composition, n_workers=worker_pool.n_workers
                )
                smallest_containing_suite_sizes[suite_rows] = composition.size
                report_rows.append(self._report_row(family, suite_rows, diversity, pool.difficulty_classes))

        return PipelineStageOutput(
            table=previous_table.with_columns(
                pl.Series("suite_family", suite_families, dtype=SUITE_MEMBERSHIP_SCHEMA["suite_family"]),
                pl.Series(
                    "smallest_containing_suite_size",
                    smallest_containing_suite_sizes,
                    dtype=SUITE_MEMBERSHIP_SCHEMA["smallest_containing_suite_size"],
                ),
            ),
            reports={SUITE_COMPOSITIONS_REPORT_NAME: pl.DataFrame(report_rows)},
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_suite(
        self, pool: CandidatePool, pool_rows: np.ndarray, composition: SuiteComposition, *, n_workers: int
    ) -> tuple[np.ndarray, float]:
        """Return the rows of the suite of `composition` that max-div selects from `pool_rows`, and its diversity score.

        `pool` holds every row of the stage's input table, and `pool_rows` and the returned rows index that table; the
        returned rows are ascending when `pool_rows` is.
        """
        solution = select_diverse_suite(
            pool.subset(pool_rows),
            composition=composition,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=n_workers,
        )
        return pool_rows[solution.i_selected], solution.score.diversity

    @staticmethod
    def _report_row(
        family: SuiteFamily, rows: np.ndarray, diversity: float | None, difficulty_classes: Sequence[DifficultyClass]
    ) -> dict[str, str | int | float | None]:
        """Return the report row of the suite of `family` that holds `rows`, selected with the score `diversity`."""
        class_counts = Counter(difficulty_classes[row] for row in rows)
        return {
            "suite_family": family.value,
            "size": len(rows),
            **{f"n_candidates_{c.value.lower()}": class_counts[c] for c in DifficultyClass},
            "diversity": diversity,
        }
