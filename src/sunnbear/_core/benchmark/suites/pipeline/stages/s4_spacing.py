"""`SpacingStage`, the fourth stage of the benchmark suite pipeline, drops near-duplicate candidates of each formula.

Dense parameter grids give candidates of 1 formula whose feature vectors lie close together. Such candidates raise the
cost of fine characterization and add little to the diversity of the benchmark suites, so the stage keeps, per formula,
only candidates that lie at least a minimum distance apart.

The stage chooses the minimum distance at which it keeps a target number of candidates.
"""

from typing import TYPE_CHECKING

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.state import NearestKeptCandidate, SpacingStateAccessor
from sunnbear._core.stats import l1_distances_to
from sunnbear._core.utils.worker_pool import WorkerPool

if TYPE_CHECKING:
    from sunnbear._core.problems.core import ProblemId

# `SpacingStage` chooses its minimum distance from these options: 10^-3.0, 10^-2.9, ... up to 10^1.0. A distance is
# measured in multiples of the mean pairwise L1 distance within a block of the coarse feature vectors, so the options
# run from 1/1000 of the mean distance, at which only nearly identical candidates are dropped, to 10 times the mean
# distance.
SPACING_MIN_DISTANCE_OPTIONS = tuple(10.0 ** (exponent_in_tenths / 10) for exponent_in_tenths in range(-30, 11))

# Fine characterization and the selection stages run on every candidate that spacing keeps, and fine characterization
# takes far longer per candidate than coarse characterization, so the target number of kept candidates sets the cost of
# the stages after spacing.
DEFAULT_SPACING_TARGET_N_KEPT_CANDIDATES = 16_384


# ==================================================================================================
#  SpacingStage
# ==================================================================================================
class SpacingStage(PipelineStage[SpacingStateAccessor]):
    """`SpacingStage` keeps, per formula, candidates that lie at least a minimum distance apart, and drops the others.

    The stage chooses the minimum distance from `SPACING_MIN_DISTANCE_OPTIONS`: the largest option at which it keeps at
    least `target_n_kept_candidates` candidates, over all formulas together. When it keeps fewer at every option, it
    takes the smallest option. The stage stores the minimum distance that it chose.

    The distance between 2 candidates is the L1 distance between their coarse feature vectors, with each block divided
    by its scale, as `SpacingStateAccessor.coarse_scaled_feature_matrix` gives them. Each block then has a mean pairwise
    distance of 1, so a minimum distance is measured in multiples of a block's mean pairwise distance.

    Per formula, a pass runs over the candidates in ascending order of their empirical difficulty index (EDI) from
    coarse characterization; candidates with equal EDIs keep the order of candidate generation, so the result is
    deterministic. The pass:

    - keeps the first and the last candidate in that order, whatever the minimum distance, so that a formula keeps its
      easiest and its hardest candidate, and a formula with 2 or more candidates keeps at least 2;
    - then keeps each candidate in between whose distance to every kept candidate, the last candidate in that order
      included, is at least the minimum distance.

    The stage drops each other candidate as a near duplicate, which is valid but not kept, and stores, for each dropped
    candidate, the nearest kept candidate of the same formula. When coarse characterization kept fewer than 2
    candidates, it has no block scales; the stage then keeps every candidate, and stores the smallest option as its
    minimum distance.

    The stage runs in the main process, not in the run's worker pool: per formula it compares a few feature vectors, and
    each worker would have to import the formulas' modules only to receive the candidates.
    """

    stage_id = PipelineStageId.SPACING

    def __init__(self, target_n_kept_candidates: int = DEFAULT_SPACING_TARGET_N_KEPT_CANDIDATES) -> None:
        """Create the stage, which aims to keep at least `target_n_kept_candidates` candidates over all formulas."""
        self.target_n_kept_candidates = target_n_kept_candidates

    @property
    def parameters(self) -> dict[str, int]:
        """Return `target_n_kept_candidates`, the stage's only parameter."""
        return {"target_n_kept_candidates": self.target_n_kept_candidates}

    def run(self, state_accessor: SpacingStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Choose the minimum distance, drop the near duplicates of each formula, and store the stage's information.

        The information is the minimum distance and the nearest kept candidate of each dropped candidate. The stage
        does not use `worker_pool`.
        """
        # --- candidates per formula, by EDI -----
        scaled_feature_matrix = state_accessor.coarse_scaled_feature_matrix()
        problem_ids_by_formula: dict[str, list[ProblemId]] = {}
        vectors_by_formula: dict[str, np.ndarray] = {}
        if scaled_feature_matrix is not None:
            edis = state_accessor.coarse_edis()
            for problem_id in scaled_feature_matrix.problem_ids:
                problem_ids_by_formula.setdefault(problem_id.formula_id, []).append(problem_id)
            for formula_id, problem_ids in problem_ids_by_formula.items():
                # The sort is stable, so candidates with equal EDIs keep the order of candidate generation.
                problem_ids.sort(key=edis.__getitem__)
                vectors_by_formula[formula_id] = scaled_feature_matrix.subset(problem_ids).values

        # --- minimum distance -------------------
        min_distance = self._choose_min_distance(list(vectors_by_formula.values()))
        state_accessor.set_min_distance(min_distance)

        # --- spacing, formula by formula --------
        nearest_kept_candidates: dict[ProblemId, NearestKeptCandidate] = {}
        for formula_id, problem_ids in problem_ids_by_formula.items():
            vectors = vectors_by_formula[formula_id]
            kept_positions = self._select_kept_positions(vectors, min_distance)
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
    def _choose_min_distance(self, vectors_per_formula: list[np.ndarray]) -> float:
        """Return the largest of `SPACING_MIN_DISTANCE_OPTIONS` at which the formulas together keep at least the target.

        Return the smallest option when the formulas keep fewer candidates than the target at every option.
        `vectors_per_formula` holds 1 array per formula, as `_select_kept_positions` takes it.

        Every option is tried, because the number of kept candidates need not fall with each larger option: the pass
        keeps a candidate by its distance to the candidates kept before it, and those change with the minimum distance.
        """
        options_reaching_target = []
        for min_distance in SPACING_MIN_DISTANCE_OPTIONS:
            n_kept = sum(len(self._select_kept_positions(vectors, min_distance)) for vectors in vectors_per_formula)
            if n_kept >= self.target_n_kept_candidates:
                options_reaching_target.append(min_distance)
        if options_reaching_target:
            return max(options_reaching_target)
        else:
            return min(SPACING_MIN_DISTANCE_OPTIONS)

    @staticmethod
    def _select_kept_positions(vectors: np.ndarray, min_distance: float) -> list[int]:
        """Return the positions in `vectors` of the candidates that 1 formula keeps at `min_distance`, ascending.

        `vectors` holds the formula's scaled feature vectors, 1 per row, in the order of the pass: ascending EDI.
        """
        last_position = len(vectors) - 1
        # A formula with 1 candidate has the same first and last position.
        kept_positions = sorted({0, last_position})
        for position in range(1, last_position):
            distances_to_kept = l1_distances_to(vectors[kept_positions], vectors[position])
            if distances_to_kept.min() >= min_distance:
                kept_positions.append(position)
        return sorted(kept_positions)
