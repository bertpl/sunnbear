"""`CandidatePool` holds the input candidates of `select_diverse_problem_ids`."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Self

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.problems.core import ProblemId

from .difficulty_tier import DifficultyTier


# ==================================================================================================
#  CandidatePool
# ==================================================================================================
@dataclass(frozen=True)
class CandidatePool:
    """A `CandidatePool` holds the candidates to select from, each with its features, EDI and tier.

    Attributes:
        feature_matrix: The candidates' scaled feature vectors from full characterization, with their ids.
        edis: Each candidate's empirical difficulty index (EDI), in the order of `feature_matrix`'s rows.
        difficulty_tiers: Each candidate's tier, in the order of `feature_matrix`'s rows.
    """

    feature_matrix: FeatureMatrix
    edis: np.ndarray
    difficulty_tiers: tuple[DifficultyTier, ...]

    def subset(self, problem_ids: Sequence[ProblemId]) -> Self:
        """Return the pool of the candidates `problem_ids`, in their order.

        Raises:
            KeyError: If 1 of `problem_ids` is not in the pool.
        """
        rows = [self.feature_matrix.row_index_by_problem_id[problem_id] for problem_id in problem_ids]
        return type(self)(
            feature_matrix=self.feature_matrix.subset(problem_ids),
            edis=self.edis[rows],
            difficulty_tiers=tuple(self.difficulty_tiers[row] for row in rows),
        )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_feature_matrix(
        cls,
        feature_matrix: FeatureMatrix,
        *,
        edis: Mapping[ProblemId, float],
        difficulty_tiers: Mapping[ProblemId, DifficultyTier],
    ) -> Self:
        """Return the pool of the candidates of `feature_matrix`, with the EDI and the tier of each, keyed by id."""
        return cls(
            feature_matrix=feature_matrix,
            edis=np.array([edis[problem_id] for problem_id in feature_matrix.problem_ids]),
            difficulty_tiers=tuple(difficulty_tiers[problem_id] for problem_id in feature_matrix.problem_ids),
        )
