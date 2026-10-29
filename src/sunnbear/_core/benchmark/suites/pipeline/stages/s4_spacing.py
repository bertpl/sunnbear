"""`SpacingStage`, the fourth stage of the benchmark suite pipeline, drops near-duplicate candidates of each formula.

Dense parameter grids give candidates of 1 formula whose feature vectors nearly coincide. Such candidates add to the
cost of full characterization and nothing to the diversity of the benchmark suites, so the stage keeps, per formula,
only candidates that lie at least a minimum distance apart.
"""

import numpy as np
import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput
from sunnbear._core.benchmark.suites.pipeline.features import FeatureFidelity
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

# The default of `SpacingStage`'s `min_distance`: a small value, which drops only candidates whose balanced feature
# vectors nearly coincide; raise it as the corpus grows, to keep full characterization's run time reasonable.
DEFAULT_SPACING_MIN_DISTANCE = 1e-3
DROPPED_CANDIDATES_REPORT_NAME = "dropped_candidates"
DROPPED_CANDIDATES_PER_FORMULA_REPORT_NAME = "dropped_candidates_per_formula"
# The report `DROPPED_CANDIDATES_REPORT_NAME` adds these columns to each dropped candidate: the kept candidate of its
# formula nearest to it, and the distance between them.
NEAREST_KEPT_CANDIDATE_SCHEMA: dict[str, pl.DataType] = {
    "nearest_kept_problem_id": pl.String(),
    "distance_to_nearest_kept": pl.Float64(),
}


# ==================================================================================================
#  SpacingStage
# ==================================================================================================
class SpacingStage(PipelineStage):
    """`SpacingStage` keeps, per formula, candidates that lie at least `min_distance` apart, and drops the others.

    The distance between 2 candidates is the L1 distance between their coarse feature vectors, with each block divided
    by its feature scale, as `FeatureFidelity.balanced_feature_vectors` returns them. Each block then has a mean
    pairwise distance of 1, so `min_distance` is a number in those units.

    Per formula, a pass runs over the candidates in the order of the input table, which is the order of candidate
    generation, so the result is deterministic. It keeps the formula's first candidate, and each later candidate whose
    distance to every candidate kept before it is at least `min_distance`. Where the pass keeps only the first of 2 or
    more candidates, the stage also keeps the candidate farthest from it, so that a formula with count candidates keeps
    at least min(2, count).

    With fewer than 2 candidates in the input, the feature scales are null, and the stage keeps every candidate.

    The stage runs in its own process, not in the run's worker pool: per formula it compares a few feature vectors, and
    each worker would have to import the formulas only to receive them.
    """

    output_name = "s4_spaced"

    def __init__(self, min_distance: float = DEFAULT_SPACING_MIN_DISTANCE) -> None:
        """Create the stage, which keeps, per formula, candidates at least `min_distance` apart."""
        self.min_distance = min_distance

    @property
    def parameters(self) -> dict[str, float]:
        """Return `min_distance`, the stage's only parameter."""
        return {"min_distance": self.min_distance}

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the kept candidates, and the reports on the dropped candidates.

        Args:
            previous_table: The output table of coarse characterization, with the feature columns and the feature
                scale columns of `FeatureFidelity.COARSE`.
            worker_pool: The worker pool of the run, which the stage does not use.

        Returns:
            The stage's output, which holds:

            - the output table: the kept rows of `previous_table`, in its order, with no added column;
            - the report `DROPPED_CANDIDATES_REPORT_NAME`: the other rows, with the columns of
              `NEAREST_KEPT_CANDIDATE_SCHEMA`;
            - the report `DROPPED_CANDIDATES_PER_FORMULA_REPORT_NAME`: 1 row per formula, in the order of each
              formula's first row in `previous_table`, with the columns ``formula_id``, ``n_candidates``, ``n_kept``
              and ``n_dropped``.
        """
        # --- rows per formula -------------------
        problem_ids = previous_table["problem_id"].to_list()
        formula_ids = [ProblemId.from_string(problem_id).formula_id for problem_id in problem_ids]
        row_indices_by_formula: dict[str, list[int]] = {}
        for row_idx, formula_id in enumerate(formula_ids):
            row_indices_by_formula.setdefault(formula_id, []).append(row_idx)

        # --- spacing, formula by formula --------
        balanced_feature_vectors = FeatureFidelity.COARSE.balanced_feature_vectors(previous_table)
        is_kept = np.zeros(previous_table.height, dtype=bool)
        nearest_kept_problem_ids: list[str | None] = [None] * previous_table.height
        distances_to_nearest_kept: list[float | None] = [None] * previous_table.height
        for row_indices in row_indices_by_formula.values():
            vectors = balanced_feature_vectors[row_indices]
            kept_positions = self._select_kept_positions(vectors)
            is_kept[[row_indices[position] for position in kept_positions]] = True
            for position, row_idx in enumerate(row_indices):
                if not is_kept[row_idx]:
                    distances_to_kept = np.abs(vectors[kept_positions] - vectors[position]).sum(axis=1)
                    nearest_idx = int(np.argmin(distances_to_kept))
                    nearest_kept_problem_ids[row_idx] = problem_ids[row_indices[kept_positions[nearest_idx]]]
                    distances_to_nearest_kept[row_idx] = float(distances_to_kept[nearest_idx])

        # --- output and reports -----------------
        is_kept_series = pl.Series("is_kept", is_kept)
        dropped_candidates = previous_table.with_columns(
            pl.Series(
                "nearest_kept_problem_id",
                nearest_kept_problem_ids,
                dtype=NEAREST_KEPT_CANDIDATE_SCHEMA["nearest_kept_problem_id"],
            ),
            pl.Series(
                "distance_to_nearest_kept",
                distances_to_nearest_kept,
                dtype=NEAREST_KEPT_CANDIDATE_SCHEMA["distance_to_nearest_kept"],
            ),
        ).filter(~is_kept_series)
        dropped_candidates_per_formula = (
            pl.DataFrame([pl.Series("formula_id", formula_ids, dtype=pl.String()), is_kept_series])
            .group_by("formula_id", maintain_order=True)
            .agg(n_candidates=pl.len(), n_kept=pl.col("is_kept").sum())
            .with_columns(n_dropped=pl.col("n_candidates") - pl.col("n_kept"))
        )
        return PipelineStageOutput(
            table=previous_table.filter(is_kept_series),
            reports={
                DROPPED_CANDIDATES_REPORT_NAME: dropped_candidates,
                DROPPED_CANDIDATES_PER_FORMULA_REPORT_NAME: dropped_candidates_per_formula,
            },
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_kept_positions(self, vectors: np.ndarray) -> list[int]:
        """Return the positions in `vectors` of the candidates that 1 formula keeps, the first position first.

        `vectors` holds the formula's balanced feature vectors, 1 per row, in the order of the input table.
        """
        kept_positions = [0]
        for position in range(1, len(vectors)):
            distances_to_kept = np.abs(vectors[kept_positions] - vectors[position]).sum(axis=1)
            if distances_to_kept.min() >= self.min_distance:
                kept_positions.append(position)
        if len(kept_positions) == 1 and len(vectors) > 1:
            # The floor of 2: the first candidate is kept, so the second is the one farthest from it among the others.
            distances_to_first = np.abs(vectors[1:] - vectors[0]).sum(axis=1)
            kept_positions.append(1 + int(np.argmax(distances_to_first)))
        return kept_positions
