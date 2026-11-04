"""`CandidatePool` holds the input candidates of `select_diverse_suite`."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Self

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.problems.core import ProblemId

from .difficulty_class import DifficultyClass


# ==================================================================================================
#  CandidatePool
# ==================================================================================================
@dataclass(frozen=True)
class CandidatePool:
    """A `CandidatePool` holds the input candidates of `select_diverse_suite`, each with its features, EDI and class.

    The EDIs and the classes follow the rows of `feature_matrix`, so each candidate's id comes with all 3.

    Attributes:
        feature_matrix: The candidates' scaled full feature vectors, with their ids.
        edis: Each candidate's empirical difficulty index (EDI), in the order of `feature_matrix`'s rows.
        difficulty_classes: Each candidate's class, in the order of `feature_matrix`'s rows.
    """

    feature_matrix: FeatureMatrix
    edis: np.ndarray
    difficulty_classes: tuple[DifficultyClass, ...]

    @property
    def problem_ids(self) -> tuple[ProblemId, ...]:
        """Return the candidates' ids, in the order of `feature_matrix`'s rows."""
        return self.feature_matrix.problem_ids

    def subset(self, problem_ids: Sequence[ProblemId]) -> Self:
        """Return the pool of the candidates `problem_ids`, in their order.

        Raises:
            KeyError: If 1 of `problem_ids` is not in the pool.
        """
        row_by_problem_id = {problem_id: row for row, problem_id in enumerate(self.problem_ids)}
        rows = [row_by_problem_id[problem_id] for problem_id in problem_ids]
        return type(self)(
            feature_matrix=self.feature_matrix.subset(problem_ids),
            edis=self.edis[rows],
            difficulty_classes=tuple(self.difficulty_classes[row] for row in rows),
        )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_candidates(
        cls,
        feature_matrix: FeatureMatrix,
        *,
        edis: Mapping[ProblemId, float],
        difficulty_classes: Mapping[ProblemId, DifficultyClass],
    ) -> Self:
        """Return the pool of the candidates of `feature_matrix`, with the EDI and the class of each, keyed by id."""
        return cls(
            feature_matrix=feature_matrix,
            edis=np.array([edis[problem_id] for problem_id in feature_matrix.problem_ids]),
            difficulty_classes=tuple(difficulty_classes[problem_id] for problem_id in feature_matrix.problem_ids),
        )
