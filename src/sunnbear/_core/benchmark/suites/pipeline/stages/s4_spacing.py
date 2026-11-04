"""`SpacingStage`, the fourth stage of the benchmark suite pipeline, drops near-duplicate candidates of each formula.

Dense parameter grids give candidates of 1 formula whose feature vectors nearly coincide. Such candidates add to the
cost of characterizing each candidate in full, and nothing to the diversity of the benchmark suites, so the stage
keeps, per formula, only candidates that lie at least a minimum distance apart.
"""

from typing import TYPE_CHECKING

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.state import NearestKeptCandidate, SpacingStateAccessor
from sunnbear._core.stats import l1_distances_to
from sunnbear._core.utils.worker_pool import WorkerPool

if TYPE_CHECKING:
    from sunnbear._core.problems.core import ProblemId

# `SpacingStage`'s default `min_distance` is small, so the stage drops only candidates whose feature vectors, with each
# block divided by its scale, nearly coincide; raise it as the corpus grows, so that characterizing the kept candidates
# in full stays affordable.
DEFAULT_SPACING_MIN_DISTANCE = 1e-3


# ==================================================================================================
#  SpacingStage
# ==================================================================================================
class SpacingStage(PipelineStage[SpacingStateAccessor]):
    """`SpacingStage` keeps, per formula, candidates that lie at least `min_distance` apart, and drops the others.

    The distance between 2 candidates is the L1 distance between their coarse feature vectors, with each block divided
    by its scale, as `SpacingStateAccessor.coarse_scaled_feature_matrix` gives them. Each block then has a mean pairwise
    distance of 1, so `min_distance` is measured in multiples of a block's mean pairwise distance.

    Per formula, a pass runs over the candidates in the order of candidate generation, so the result is deterministic.
    The pass keeps the formula's first candidate, and each later candidate whose distance to every candidate kept
    before it is at least `min_distance`.

    Where a formula has 2 or more candidates and the pass keeps only its first, the stage also keeps the candidate
    farthest from it, so that a formula with 2 or more candidates keeps at least 2.

    The stage drops each other candidate as a near duplicate, which is valid but not kept, and stores, for each dropped
    candidate, the nearest kept candidate of the same formula. Without scales, which coarse characterization lacks
    when it kept fewer than 2 candidates, the stage keeps every candidate.

    The stage runs in the main process, not in the run's worker pool: per formula it compares a few feature vectors, and
    each worker would have to import the formulas' modules only to receive the candidates.
    """

    stage_id = PipelineStageId.SPACING

    def __init__(self, min_distance: float = DEFAULT_SPACING_MIN_DISTANCE) -> None:
        """Create the stage, which keeps, per formula, candidates at least `min_distance` apart.

        `min_distance` is measured in multiples of a feature block's mean pairwise L1 distance.
        """
        self.min_distance = min_distance

    @property
    def parameters(self) -> dict[str, float]:
        """Return `min_distance`, the stage's only parameter."""
        return {"min_distance": self.min_distance}

    def run(self, state_accessor: SpacingStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Drop the near duplicates of each formula, and store the nearest kept candidate of each dropped one.

        The stage does not use `worker_pool`.
        """
        scaled_feature_matrix = state_accessor.coarse_scaled_feature_matrix()
        nearest_kept_candidates: dict[ProblemId, NearestKeptCandidate] = {}
        if scaled_feature_matrix is not None:
            # --- candidates per formula ---------
            problem_ids_by_formula: dict[str, list[ProblemId]] = {}
            for problem_id in scaled_feature_matrix.problem_ids:
                problem_ids_by_formula.setdefault(problem_id.formula_id, []).append(problem_id)

            # --- spacing, formula by formula ----
            for problem_ids in problem_ids_by_formula.values():
                vectors = scaled_feature_matrix.subset(problem_ids).values
                kept_positions = self._select_kept_positions(vectors)
                for position, problem_id in enumerate(problem_ids):
                    if position not in kept_positions:
                        distances_to_kept = l1_distances_to(vectors[kept_positions], vectors[position])
                        nearest_idx = int(np.argmin(distances_to_kept))
                        nearest_kept_candidates[problem_id] = NearestKeptCandidate(
                            problem_id=problem_ids[kept_positions[nearest_idx]],
                            distance=float(distances_to_kept[nearest_idx]),
                        )
                        state_accessor.drop(problem_id, "near_duplicate")
        state_accessor.set_nearest_kept_candidates(nearest_kept_candidates)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_kept_positions(self, vectors: np.ndarray) -> list[int]:
        """Return the positions in `vectors` of the candidates that 1 formula keeps, in ascending order.

        `vectors` holds the formula's scaled feature vectors, 1 per row, in the order of candidate generation.
        """
        kept_positions = [0]
        for position in range(1, len(vectors)):
            distances_to_kept = l1_distances_to(vectors[kept_positions], vectors[position])
            if distances_to_kept.min() >= self.min_distance:
                kept_positions.append(position)
        if len(kept_positions) == 1 and len(vectors) > 1:
            # Keep at least 2 candidates: the first is already kept, so add the one farthest from it among the others.
            distances_to_first = l1_distances_to(vectors[1:], vectors[0])
            kept_positions.append(1 + int(np.argmax(distances_to_first)))
        return kept_positions
