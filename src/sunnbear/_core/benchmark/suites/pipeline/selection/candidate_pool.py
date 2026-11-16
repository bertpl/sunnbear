"""`CandidatePool` holds the input candidates of `select_diverse_problem_ids`."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cached_property
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
    """A `CandidatePool` holds the candidates to select from, each with its features and EDI.

    Attributes:
        feature_matrix: The candidates' scaled feature vectors from fine characterization, with their ids.
        edis: Each candidate's empirical difficulty index (EDI), in the order of `feature_matrix`'s rows.
        n_bisection_fevals: The `n_bisection_fevals` of the solves that gave the EDIs, which sets the tiers' EDI ranges.
    """

    feature_matrix: FeatureMatrix
    edis: np.ndarray
    n_bisection_fevals: int

    @cached_property
    def difficulty_tiers(self) -> dict[ProblemId, DifficultyTier]:
        """Return each candidate's difficulty tier, from its EDI, keyed by id in the order of the pool."""
        return {
            problem_id: DifficultyTier.from_edi(edi, n_bisection_fevals=self.n_bisection_fevals)
            for problem_id, edi in zip(self.feature_matrix.problem_ids, self.edis, strict=True)
        }

    def subset(self, problem_ids: Sequence[ProblemId]) -> Self:
        """Return the pool of the candidates `problem_ids`, in their order.

        Raises:
            KeyError: If 1 of `problem_ids` is not in the pool.
        """
        rows = [self.feature_matrix.row_index_by_problem_id[problem_id] for problem_id in problem_ids]
        return type(self)(
            feature_matrix=self.feature_matrix.subset(problem_ids),
            edis=self.edis[rows],
            n_bisection_fevals=self.n_bisection_fevals,
        )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_feature_matrix(
        cls, feature_matrix: FeatureMatrix, *, edis: Mapping[ProblemId, float], n_bisection_fevals: int
    ) -> Self:
        """Return the pool of the candidates of `feature_matrix`, with the EDI of each, keyed by id."""
        return cls(
            feature_matrix=feature_matrix,
            edis=np.array([edis[problem_id] for problem_id in feature_matrix.problem_ids]),
            n_bisection_fevals=n_bisection_fevals,
        )
